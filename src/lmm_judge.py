import os
import time
import json
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from load_longvideobench import LongVideoBenchDataset
from call_gpt4o import request
from utils import dump_jsonl

# Prompts dictionary
PROMPTS = {
    "role": """**Remember: You are watching a Video.**

A user, characterized by a specific persona, is interacting with two AI assistant models (A and B) to better understand video content using the same question. Here is the user's persona:
```persona
{persona}
```

The user's question is:
```question
{question}
```

The response from Model A is:
```model_a
{answer_a}
```

The response from Model B is:
```model_b
{answer_b}
```

Please act as an impartial judge and carefully evaluate the responses of Model A and Model B to determine which one is better. Use the following standards:

1. [Instruction Following]: The response should closely adhere to the user's instructions, ensuring it directly addresses the specified task.
2. [Accuracy]: The response must accurately utilize information from the video, avoiding fabrication or misquotation. It should maintain factual correctness, avoid hallucinations, and demonstrate contextual coherence with precise terminology and knowledge.
3. [Relevance]: The response should consider the user's background information and needs, providing a comprehensive, detailed answer that addresses the question directly without straying off-topic. Responses should be thorough, offering multiple perspectives where relevant.
4. [Helpfulness]: The response should provide valuable information to aid the user in understanding or solving their issue, avoiding irrelevant or vague content.

If the responses from Model A and Model B are of similar quality (whether both are good or both are bad), you may declare a tie.

**Please follow these steps for your judgment:**

- Step 1: Analyze which model provides a better response for the [Instruction Following] standard.
- Step 2: Analyze which model provides a better response for the [Accuracy] standard.
- Step 3: Analyze which model provides a better response for the [Relevance] standard.
- Step 4: Analyze which model provides a better response for the [Helpfulness] standard.
- Step 5: Based on the results from Steps 1-4, you must output only one of the following choices as your
final verdict with a label:
1. Model A is better: [[A>B]]
2. Tie, relatively the same: [[A=B]]
3. Model B is better: [[B>A]]
Example output: "My final verdict is tie: [[A=B]]".

Please respond strictly in the following format:

```[Instruction Following]
[Your Analysis]
```

```[Accuracy]
[Your Analysis]
```

```[Relevance]
[Your Analysis]
```

```[Helpfulness]
[Your Analysis]
```

```[Overall Judge]
[Your Judge]
```""",
}


# Global variable for video_data
video_data = LongVideoBenchDataset(os.getenv('LVB_PATH'), "lvb_test_wo_gt.json", max_num_frames=128)

def run_one_prompt(paths):
    """
    Process a single prompt and save the result.

    Args:
        paths (tuple): A tuple containing the index, sample data, and output directory.
    """
    idx, sample, output_dir = paths
    qid = sample["qid"]
    video_id = sample["video_id"]
    persona = sample["persona"]
    question = sample["question"]
    model_a_answer = sample["reference"]
    model_b_answer = sample["response"]
    output_path = os.path.join(output_dir, f'{qid}.jsonl')

    if os.path.exists(output_path):
        print(f'{output_path} already exists, skipping...')
        return

    video_inputs = video_data.get_w_video_id(video_id)["inputs"]

    try:
        chosen_prompt = PROMPTS['role'].format(
            persona=persona,
            question=question,
            answer_a=model_a_answer,
            answer_b=model_b_answer
        )
        response = request(
            video_inputs=video_inputs,
            prompt=chosen_prompt,
        )
        sample["GPT4o Judge response"] = response
        dump_jsonl([sample], output_path)
        print(f'Saved {output_path}')

    except Exception as e:
        print(f"Error: {e}")
        print(f"Error on video: {video_id}")
        print(f"Error on output_path: {output_path}")


def multi_process_request(data, output_dir, worker_num=10):
    """
    Process multiple prompts in parallel using multi-processing.

    Args:
        data (list): List of samples to process.
        output_dir (str): Directory to store the output results.
        worker_num (int): Number of workers for multi-processing.
    """
    total_samples = len(data)
    print(f"Total samples: {total_samples}")

    with ProcessPoolExecutor(max_workers=worker_num) as executor:
        start_time = time.time()
        count = 0
        futures = [executor.submit(run_one_prompt, (idx, obj, output_dir)) for idx, obj in enumerate(data)]

        for job in as_completed(futures):
            job.result(timeout=None)
            end_time = time.time()
            average_time = (end_time - start_time) / (count + 1)
            count += 1

            if count % 100 == 0:
                print(
                    f"[worker_num={worker_num}] Processed {count} lines, "
                    f"average time: {average_time:.2f}s, "
                    f"expected time: {average_time / 60 * (total_samples - count):.2f}min"
                )

    print(f'Finished processing {total_samples} samples in {time.time() - start_time:.2f} seconds')


def make_sample_data(vab_path, ans_path, mode):
    """
    Load and prepare sample data from the battle file.

    Args:
        vab_path (str): Path to the VideoAutoBench data file.
        ans_path (str): Path to the models' answers file.
        mode (str): Compare with selected or rejected responses.

    Returns:
        list: List of prepared samples.
    """
    vab = json.load(open(vab_path, "r"))
    answers = json.load(open(ans_path, "r"))
    data = []
    for qid in answers:
        sample = answers[qid]
        if mode == "selected":
            sample["reference"] = vab[qid]["selected answer"]
        elif mode == "rejected":
            sample["reference"] = vab[qid]["rejected answer"]
        else:
            raise ValueError("Invalid mode. Choose either 'selected' or 'rejected'.")
        sample["qid"] = qid
        data.append(sample)
    return data


def main():
    """
    Main function to parse arguments and start the processing.
    """
    parser = argparse.ArgumentParser(description="Process video QA with different models.")
    parser.add_argument("--vab_path", type=str, required=True, help="Path to the VideoAutoBench data.")
    parser.add_argument("--ans_path", type=str, required=True, help="Path to the models' answers file.")
    parser.add_argument("--mode", type=str, default="selected", choices=["selected", "rejected"], help="Mode to determine the scoring logic.")
    parser.add_argument("--output_dir", type=str, required=True, help="Directory to store the output results.")
    parser.add_argument("--worker_num", type=int, default=8, help="Number of workers for multi-processing.")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    data = make_sample_data(args.vab_path, args.ans_path, args.mode)

    multi_process_request(data, args.output_dir, worker_num=args.worker_num)


if __name__ == "__main__":
    main()