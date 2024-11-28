import os
import json
import argparse

def load_data(input_dir, vab, mode="selected"):
    """
    Load and process data from the input directory.

    Args:
        input_dir (str): Path to the input directory.
        vab (dict): VideoAutoBench data.
        mode (str): Mode to determine the scoring logic.

    Returns:
        tuple: A tuple containing the number of wins (w) and the total number of samples (total).
    """
    w, total = 0, 0

    for file in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file)
        try:
            with open(file_path, "r") as f:
                tmp = json.load(f)
                qid = tmp["qid"]

                if qid not in vab:
                    raise ValueError(f"QID {qid} not found in VideoAutoBench data.")

                judge = tmp["GPT4o Judge response"].split("[Overall Judge]")[-1]

                if "B>A" in judge:
                    w += 1
                elif "=" in judge:
                    if mode == "selected":
                        w += 0.5

                total += 1

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error processing file {file_path}: {e}")

    return w, total

def main():
    parser = argparse.ArgumentParser(description="Calculate win rate based on GPT4o Judge responses.")
    parser.add_argument("--input_dir", type=str, required=True, help="Path to the input directory.")
    parser.add_argument("--mode", type=str, default="selected", choices=["selected", "rejected"], help="Mode to determine the scoring logic.")
    parser.add_argument("--vab_path", type=str, required=True, help="Path to the VideoAutoBench data.")

    args = parser.parse_args()
    input_dir = args.input_dir
    mode = args.mode

    # Load VideoAutoBench data
    with open(args.vab_path, "r") as f:
        vab = json.load(f)

    # Load and process data
    w, total = load_data(input_dir, vab, mode)

    # Calculate and print the win rate
    win_rate = w / total if total > 0 else 0
    print(f"Mode: {mode.capitalize()}")
    print(f"Total samples: {total}")
    print(f"Wins: {w}")
    print(f"Win rate: {win_rate:.2%}")

if __name__ == "__main__":
    main()