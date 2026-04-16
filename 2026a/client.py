import socket
import sys
import time
import getpass
import os
import json
import threading

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.rule import Rule
from rich import box

#SERVER_IP = '10.171.159.254'
SERVER_IP = '10.171.132.99'
SERVER_PORT = 65432
SOCKET_TIMEOUT = 30
RECONNECT_DELAY = 3
IDLE_TIMEOUT = 60  # seconds
MAX_PROMPT_LENGTH = 256  # bytes

console = Console()

patients = [
    [1, "Julian"],
    [2, "Emily"],
    [3, "Sophia"],
    [4, "Camila"],
    [5, "Connor"],
    [6, "Ben"],
    [7, "Aidan"],
    [8, "Emma"],
    [9, "Lizzy"],
    [10, "Michaela"],
    [11, "Ian"],
    [12, "Samira"],
    [13, "Ethan"],
    [14, "Jackson"],
    [15, "Cynthia"],
    [16, "Olivia"],
    [17, "Leo"],
    [18, "Zoe"],
    [19, "Tyler"],
    [20, "Riley"],
    [21, "Mason"],
]

# SAMPLE assessment state
SAMPLE_LABELS = {
    "S": "Signs & Symptoms",
    "A": "Allergies",
    "M": "Medications",
    "P": "Past History",
    "L": "Last Intake",
    "E": "Events Leading Up",
}

# Session state
sample_covered = set()
vitals_revealed = False
vitals_data = None
start_time = None
conversation_log = []  # list of (role, text) tuples

last_activity = time.time()
idle_lock = threading.Lock()
idle_triggered = threading.Event()


# ─── Display helpers ───────────────────────────────────────────────

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print the MedSim AI welcome banner."""
    banner = Text()
    banner.append("  +  ", style="bold red")
    banner.append("MedSim AI", style="bold cyan")
    banner.append("  +  ", style="bold red")
    banner.append("  CNA Training Simulator", style="dim white")
    console.print(Panel(banner, border_style="cyan", box=box.DOUBLE))


def print_header(patient_name):
    """Print the patient header with timer."""
    elapsed = ""
    if start_time:
        secs = int(time.time() - start_time)
        mins, s = divmod(secs, 60)
        elapsed = f"{mins}:{s:02d}"

    header = Table.grid(padding=(0, 3))
    header.add_column(justify="left", min_width=30)
    header.add_column(justify="right", min_width=20)
    header.add_row(
        Text.assemble(
            ("  +  ", "bold red"),
            ("Patient: ", "dim white"),
            (patient_name, "bold cyan"),
        ),
        Text.assemble(
            ("Time: ", "dim white"),
            (elapsed, "bold white"),
        ),
    )
    console.print(Panel(header, border_style="cyan", title="[bold cyan]MedSim AI[/]", title_align="left", box=box.ROUNDED))


def print_sample_checklist():
    """Print the SAMPLE assessment checklist."""
    table = Table(
        title="[bold white]SAMPLE Assessment[/]",
        box=box.SIMPLE,
        show_header=False,
        title_style="bold white",
        padding=(0, 1),
    )
    table.add_column("Check", width=3)
    table.add_column("Category", min_width=20)

    for letter, label in SAMPLE_LABELS.items():
        if letter in sample_covered:
            check = "[bold green][x][/]"
            style = "green"
        else:
            check = "[dim][ ][/]"
            style = "dim white"
        table.add_row(check, f"[{style}]{letter} - {label}[/]")

    return table


def print_vitals_panel(patient_name):
    """Print the vitals panel (hidden or revealed)."""
    table = Table(
        title="[bold white]Vitals[/]",
        box=box.SIMPLE,
        show_header=False,
        title_style="bold white",
        padding=(0, 1),
    )
    table.add_column("Label", min_width=12)
    table.add_column("Value", min_width=18)

    if vitals_revealed and vitals_data:
        for label, value in vitals_data.items():
            is_abnormal = any(tag in value for tag in ("elevated", "low", "HIGH", "LOW"))
            style = "bold red" if is_abnormal else "white"
            table.add_row(f"[dim white]{label}:[/]", f"[{style}]{value}[/]")
    else:
        for label in ["HR", "Temp", "BP", "SpO2", "Resp"]:
            table.add_row(f"[dim white]{label}:[/]", "[dim]--[/]")
        if not vitals_revealed:
            table.add_row("", "[dim italic]Type .vitals to reveal[/]")

    return table


def print_sidebar(patient_name):
    """Print SAMPLE checklist and vitals side by side."""
    sample_table = print_sample_checklist()
    vitals_table = print_vitals_panel(patient_name)
    console.print(Columns([sample_table, vitals_table], padding=(0, 4)))


def print_help_bar():
    """Print the command help bar at the bottom."""
    help_text = Text()
    commands = [
        (".vitals", "Request vitals"),
        (".reset", "Reset mood"),
        (".dx", "Submit diagnosis"),
        (".switch", "Change patient"),
        ("exit", "Quit"),
    ]
    for i, (cmd, desc) in enumerate(commands):
        if i > 0:
            help_text.append("  |  ", style="dim")
        help_text.append(cmd, style="bold cyan")
        help_text.append(f" {desc}", style="dim white")
    console.print(Panel(help_text, border_style="dim", box=box.ROUNDED))


def print_conversation_tail(patient_name, n=6):
    """Print the last n conversation exchanges."""
    recent = conversation_log[-n:]
    if not recent:
        console.print(Panel(
            "[dim italic]Start by asking the patient a question...[/]",
            title="[bold white]Conversation[/]",
            border_style="dim cyan",
            box=box.ROUNDED,
        ))
        return

    text = Text()
    for role, msg in recent:
        if role == "doctor":
            text.append("Doctor: ", style="bold green")
            text.append(msg + "\n", style="white")
        elif role == "patient":
            text.append(f"{patient_name}: ", style="bold cyan")
            text.append(msg + "\n", style="white")
        elif role == "system":
            text.append(msg + "\n", style="dim yellow")
    console.print(Panel(
        text,
        title="[bold white]Conversation[/]",
        border_style="dim cyan",
        box=box.ROUNDED,
    ))


def redraw_screen(patient_name):
    """Redraw the full TUI screen."""
    clear_screen()
    print_header(patient_name)
    console.print()
    print_sidebar(patient_name)
    console.print()
    print_conversation_tail(patient_name)
    console.print()
    print_help_bar()


def print_score_card(patient_name, dx_result):
    """Print the final assessment score card."""
    from scoring import calculate_score, SAMPLE_LABELS as S_LABELS

    score = calculate_score(sample_covered, dx_result)

    # Build the score card
    card = Text()
    card.append(f"\n  Patient: {patient_name}\n", style="bold white")

    elapsed = ""
    if start_time:
        secs = int(time.time() - start_time)
        mins, s = divmod(secs, 60)
        elapsed = f"{mins}:{s:02d}"
    card.append(f"  Time: {elapsed}\n\n", style="dim white")

    pct = int(score["sample_count"] / score["sample_total"] * 100)
    card.append(f"  SAMPLE Coverage:  {score['sample_count']}/{score['sample_total']}  ({pct}%)", style="white")
    card.append(f"    +{score['sample_score']} pts\n", style="bold yellow")

    # Show checklist inline
    for letter, label in SAMPLE_LABELS.items():
        if letter in sample_covered:
            card.append(f"    [x] {letter}\n", style="green")
        else:
            card.append(f"    [ ] {letter}\n", style="dim")

    card.append(f"\n  Diagnosis: \"{dx_result[2]}\"\n", style="white")
    result_style = {"correct": "bold green", "partial": "bold yellow", "wrong": "bold red"}
    card.append(f"  Result: {dx_result[0].upper()}", style=result_style.get(dx_result[0], "white"))
    card.append(f"    +{dx_result[1]} pts\n\n", style="bold yellow")

    card.append(f"  Total Score: {score['total']} / {score['max_total']}\n", style="bold white")
    tier_style = "bold green" if score["total"] >= 90 else "bold yellow" if score["total"] >= 50 else "bold red"
    card.append(f"  Rating: {score['tier']}\n", style=tier_style)

    console.print(Panel(
        card,
        title="[bold white]Assessment Complete[/]",
        border_style="bold cyan",
        box=box.DOUBLE,
    ))


# ─── Networking ────────────────────────────────────────────────────

def stream_response(sock):
    """Yield text tokens from the server, handle special tags."""
    buffer = bytearray()
    while True:
        try:
            chunk = sock.recv(64)
            if not chunk:
                raise ConnectionError("Server closed connection.")
            buffer.extend(chunk)
            while True:
                try:
                    decoded = buffer.decode('utf-8')

                    # Check for end of response
                    if "<<END_OF_RESPONSE>>" in decoded:
                        idx = decoded.index("<<END_OF_RESPONSE>>")
                        to_yield = decoded[:idx]
                        remainder = decoded[idx + len("<<END_OF_RESPONSE>>"):]

                        if to_yield:
                            yield ("text", to_yield)

                        # Check remainder for special tags
                        parse_special_tags(remainder)
                        return

                    # Check for special tags within the stream
                    tag_start = decoded.find("<<")
                    if tag_start > 0:
                        # Yield text before the tag
                        yield ("text", decoded[:tag_start])
                        buffer = bytearray(decoded[tag_start:].encode('utf-8'))
                    elif tag_start == 0 and ">>" in decoded:
                        # Full tag in buffer
                        tag_end = decoded.index(">>") + 2
                        tag = decoded[:tag_end]
                        parse_special_tags(tag)
                        buffer = bytearray(decoded[tag_end:].encode('utf-8'))
                    elif tag_start == -1 and decoded:
                        yield ("text", decoded)
                        buffer.clear()
                    else:
                        # Incomplete tag, wait for more data
                        pass
                    break
                except UnicodeDecodeError as e:
                    valid_up_to = e.start
                    if valid_up_to > 0:
                        part = buffer[:valid_up_to].decode('utf-8', errors='replace')
                        yield ("text", part)
                        buffer = buffer[valid_up_to:]
                    break
        except (socket.timeout, ConnectionResetError):
            raise TimeoutError("Timed out waiting for server response.")
        except Exception as e:
            raise ConnectionError(f"Server closed connection: {str(e)}")


def parse_special_tags(text):
    """Parse special server tags like <<SAMPLE:SE>>, <<VITALS:{...}>>, <<DX:{...}>>."""
    global sample_covered, vitals_revealed, vitals_data

    import re
    # SAMPLE tag
    sample_match = re.search(r'<<SAMPLE:([A-Z]+)>>', text)
    if sample_match:
        for letter in sample_match.group(1):
            if letter in SAMPLE_LABELS:
                sample_covered.add(letter)

    # VITALS tag
    vitals_match = re.search(r'<<VITALS:(\{.*?\})>>', text)
    if vitals_match:
        try:
            vitals_data = json.loads(vitals_match.group(1))
            vitals_revealed = True
        except json.JSONDecodeError:
            pass

    # DX tag (diagnosis result) — handled by caller
    dx_match = re.search(r'<<DX:(\{.*?\})>>', text)
    if dx_match:
        try:
            return json.loads(dx_match.group(1))
        except json.JSONDecodeError:
            pass
    return None


def connect_to_server(scenario):
    while True:
        try:
            console.print(f"[dim]Connecting to server...[/]")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(SOCKET_TIMEOUT)
            sock.connect((SERVER_IP, SERVER_PORT))
            sock.sendall(str(scenario).encode('utf-8'))
            patient_name = sock.recv(1024).decode('utf-8', errors='replace').strip()
            console.print(f"[green]Connected.[/] Patient: [bold cyan]{patient_name}[/]")
            return sock, patient_name
        except Exception as e:
            console.print(f"[red]Connection failed ({e}), retrying in {RECONNECT_DELAY}s...[/]")
            time.sleep(RECONNECT_DELAY)


def reconnect_and_resend(scenario, last_query):
    while True:
        sock, patient_name = connect_to_server(scenario)
        try:
            sock.sendall(last_query.encode('utf-8'))
            return sock, patient_name
        except Exception as e:
            console.print(f"[red]Resend failed: {e}. Retrying...[/]")
            sock.close()
            time.sleep(RECONNECT_DELAY)


def send_and_receive(sock, message):
    """Send a message and collect the full streaming response. Returns response text."""
    sock.sendall(message.encode('utf-8'))
    full_text = ""
    for tag_type, content in stream_response(sock):
        if tag_type == "text":
            full_text += content
    return full_text


# ─── Scenario selection ────────────────────────────────────────────

def choose_scenario():
    clear_screen()
    print_banner()
    console.print()
    console.print("[bold white]  Select a Patient[/]")
    console.print()

    # Display patients in a nice grid
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 2))
    table.add_column("#", justify="right", style="bold cyan", width=3)
    table.add_column("Patient", min_width=12, style="white")
    table.add_column("#", justify="right", style="bold cyan", width=3)
    table.add_column("Patient", min_width=12, style="white")
    table.add_column("#", justify="right", style="bold cyan", width=3)
    table.add_column("Patient", min_width=12, style="white")

    # Arrange in 3 columns
    rows = []
    for i in range(0, len(patients), 3):
        row = []
        for j in range(3):
            if i + j < len(patients):
                p = patients[i + j]
                row.extend([str(p[0]), p[1]])
            else:
                row.extend(["", ""])
        rows.append(row)

    for row in rows:
        table.add_row(*row)

    console.print(table)
    console.print()

    while True:
        try:
            choice = console.input("[bold cyan]Choose patient (1-21): [/]")
            scenario = int(choice.strip())
            if 1 <= scenario <= 21:
                return scenario
            console.print("[red]Invalid choice. Pick 1-21.[/]")
        except ValueError:
            console.print("[red]Numbers only please.[/]")


# ─── Idle mumble thread ───────────────────────────────────────────

def idle_mumble_thread(sock_ref, patient_name_ref, scenario_ref):
    global last_activity
    while True:
        time.sleep(1)
        if idle_triggered.is_set():
            continue
        if time.time() - last_activity > IDLE_TIMEOUT:
            idle_triggered.set()
            with idle_lock:
                try:
                    sock = sock_ref[0]
                    patient_name = patient_name_ref[0]
                    scenario = scenario_ref[0]
                    sock.sendall("...".encode('utf-8'))
                    response_text = ""
                    console.print(f"\n[bold cyan]{patient_name}:[/] ", end="")
                    for tag_type, content in stream_response(sock):
                        if tag_type == "text":
                            console.print(content, end="")
                            response_text += content
                    console.print()
                    if response_text.strip():
                        conversation_log.append(("patient", response_text.strip()))
                except Exception as e:
                    console.print(f"\n[dim red]Idle mumble failed: {e}. Reconnecting...[/]")
                    sock, patient_name = reconnect_and_resend(scenario, "...")
                    sock_ref[0] = sock
                    patient_name_ref[0] = patient_name
                    response_text = ""
                    console.print(f"\n[bold cyan]{patient_name}:[/] ", end="")
                    for tag_type, content in stream_response(sock):
                        if tag_type == "text":
                            console.print(content, end="")
                            response_text += content
                    console.print()
                    if response_text.strip():
                        conversation_log.append(("patient", response_text.strip()))
                last_activity = time.time()
            idle_triggered.clear()


# ─── Diagnosis flow ───────────────────────────────────────────────

def handle_diagnosis(sock, patient_name):
    """Handle the .dx diagnosis submission flow."""
    console.print()
    console.print(Panel(
        "[bold white]Submit your diagnosis for this patient.[/]\n"
        "[dim]Type your best guess at what condition they have.[/]",
        border_style="cyan",
        box=box.ROUNDED,
    ))

    guess = console.input("[bold cyan]Your diagnosis: [/]").strip()
    if not guess:
        console.print("[dim]Diagnosis cancelled.[/]")
        return None

    # Send to server for checking
    sock.sendall(f".dx:{guess}".encode('utf-8'))

    # Read response and parse DX tag
    buffer = bytearray()
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buffer.extend(chunk)
        decoded = buffer.decode('utf-8', errors='replace')
        if "<<END_OF_RESPONSE>>" in decoded:
            break

    decoded = buffer.decode('utf-8', errors='replace')
    import re
    dx_match = re.search(r'<<DX:(\{.*?\})>>', decoded)
    if dx_match:
        try:
            dx_data = json.loads(dx_match.group(1))
            result = dx_data.get("result", "wrong")
            points = dx_data.get("points", 0)
            return (result, points, guess)
        except json.JSONDecodeError:
            pass

    console.print("[red]Could not process diagnosis. Try again.[/]")
    return None


# ─── Vitals flow ──────────────────────────────────────────────────

def handle_vitals(sock, patient_name):
    """Request and display patient vitals."""
    global vitals_revealed, vitals_data

    sock.sendall(b".vitals")

    buffer = bytearray()
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        buffer.extend(chunk)
        decoded = buffer.decode('utf-8', errors='replace')
        if "<<END_OF_RESPONSE>>" in decoded:
            break

    decoded = buffer.decode('utf-8', errors='replace')
    import re
    vitals_match = re.search(r'<<VITALS:(\{.*?\})>>', decoded)
    if vitals_match:
        try:
            vitals_data = json.loads(vitals_match.group(1))
            vitals_revealed = True
        except json.JSONDecodeError:
            console.print("[red]Could not parse vitals.[/]")


# ─── Reset session state ──────────────────────────────────────────

def reset_session():
    """Reset all session state for a new patient."""
    global sample_covered, vitals_revealed, vitals_data, start_time, conversation_log
    sample_covered = set()
    vitals_revealed = False
    vitals_data = None
    start_time = time.time()
    conversation_log = []


# ─── Main ─────────────────────────────────────────────────────────

def main():
    global last_activity, start_time

    clear_screen()
    print_banner()
    console.print()
    password = getpass.getpass("Enter password: ")
    if password != "":
        console.print("[bold red]Incorrect password. Exiting.[/]")
        sys.exit(1)

    scenario = choose_scenario()
    reset_session()

    sock, patient_name = connect_to_server(scenario)
    redraw_screen(patient_name)

    # For mutable references in the idle thread
    sock_ref = [sock]
    patient_name_ref = [patient_name]
    scenario_ref = [scenario]

    threading.Thread(
        target=idle_mumble_thread,
        args=(sock_ref, patient_name_ref, scenario_ref),
        daemon=True,
    ).start()

    last_query = None
    empty_input_count = 0
    EMPTY_INPUT_THRESHOLD = 3
    last_prompt_time = 0
    PROMPT_COOLDOWN = 7  # seconds

    while True:
        try:
            query = console.input("\n[bold green]Doctor > [/]").strip()
            last_activity = time.time()

            if len(query.encode('utf-8')) > MAX_PROMPT_LENGTH:
                console.print(f"[red]Prompt too long! Limit is {MAX_PROMPT_LENGTH} bytes.[/]")
                continue

            if query == '':
                empty_input_count += 1
                if empty_input_count >= EMPTY_INPUT_THRESHOLD:
                    console.print("[dim yellow]Please type a question for the patient.[/]")
                continue
            else:
                empty_input_count = 0

            if query.lower() == 'exit':
                console.print("[dim]Goodbye![/]")
                break

            # ── .switch command ──
            if query.lower() == '.switch':
                sock.close()
                scenario = choose_scenario()
                reset_session()
                sock, patient_name = connect_to_server(scenario)
                sock_ref[0] = sock
                patient_name_ref[0] = patient_name
                scenario_ref[0] = scenario
                redraw_screen(patient_name)
                continue

            # ── .vitals command ──
            if query.lower() == '.vitals':
                if vitals_revealed:
                    console.print("[dim]Vitals already displayed above.[/]")
                else:
                    handle_vitals(sock, patient_name)
                redraw_screen(patient_name)
                continue

            # ── .dx command ──
            if query.lower() == '.dx':
                dx_result = handle_diagnosis(sock, patient_name)
                if dx_result:
                    clear_screen()
                    print_score_card(patient_name, dx_result)
                    console.print()
                    console.input("[dim]Press Enter to continue...[/]")
                    redraw_screen(patient_name)
                continue

            # ── .reset command ──
            if query.lower() == '.reset':
                last_query = query
                sock.sendall(query.encode('utf-8'))
                response_text = ""
                for tag_type, content in stream_response(sock):
                    if tag_type == "text":
                        response_text += content
                conversation_log.append(("system", response_text.strip()))
                redraw_screen(patient_name)
                continue

            # ── Rate limiting ──
            current_time = time.time()
            if current_time - last_prompt_time < PROMPT_COOLDOWN:
                wait_time = PROMPT_COOLDOWN - (current_time - last_prompt_time)
                console.print(f"[dim yellow]Please wait {wait_time:.1f}s before your next question.[/]")
                continue
            last_prompt_time = current_time

            # ── Regular question ──
            last_query = query
            conversation_log.append(("doctor", query))

            while True:
                try:
                    sock.sendall(query.encode('utf-8'))
                    response_text = ""
                    console.print(f"\n[bold cyan]{patient_name}:[/] ", end="")
                    for tag_type, content in stream_response(sock):
                        if tag_type == "text":
                            console.print(content, end="", highlight=False)
                            response_text += content
                    console.print()

                    if response_text.strip():
                        conversation_log.append(("patient", response_text.strip()))

                    # Show updated SAMPLE coverage after each question
                    if sample_covered:
                        covered_str = ", ".join(
                            SAMPLE_LABELS[l] for l in sorted(sample_covered)
                        )
                        console.print(f"[dim green]  SAMPLE: {len(sample_covered)}/6 covered ({covered_str})[/]")

                    break  # Success
                except (TimeoutError, ConnectionError) as e:
                    console.print(f"\n[red]Lost connection: {e}. Reconnecting...[/]")
                    sock.close()
                    sock, patient_name = reconnect_and_resend(scenario, last_query)
                    sock_ref[0] = sock
                    patient_name_ref[0] = patient_name
                    console.print("[green]Reconnected.[/]")

            idle_triggered.clear()

        except KeyboardInterrupt:
            console.print("\n[dim]Exiting.[/]")
            break

    sock.close()


if __name__ == '__main__':
    main()
