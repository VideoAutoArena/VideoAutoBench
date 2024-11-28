# VideoAutoBench

| [📄 Paper](https://arxiv.org/abs/2411.13281) | [🌐 Project Page](https://videoautoarena.github.io/) |

**VideoAutoBench** provides a set of challenging open-ended questions designed to evaluate multimodal chat assistants in video analysis. It blends the **user-centric evaluation** of [VideoAutoArena]() with the **efficiency and simplicity** of traditional benchmarks. 

### Key Features:
- **Judging Model**: Utilizes GPT-4o for scoring model responses.
- **Scoring Criteria**:
  - **Against human-selected answers**:  
    - 1 point for a win  
    - 0.5 for a tie  
    - 0 for a loss  
  - **Against human-rejected answers**:  
    - Only a win earns 1 point  
- **Final Score**: Average of all scores across the benchmark.



## 🛠️ Installation

Follow these steps to set up VideoAutoBench:

```bash
git clone https://github.com/VideoAutoArena/VideoAutoBench.git
cd VideoAutoBench
pip install -r requirements.txt
```

This will clone the repository and install the necessary dependencies from the `requirements.txt` file.



## 🎯 Evaluation

### Step 1: Generate Model Answers

This step involves generating answers for the VideoAutoBench questions using your own large multimodal models (LMMs).

1. **Obtain the LongVideoBench Dataset**  
   First, download and set up the LongVideoBench dataset by following the [instructions here](https://github.com/longvideobench/LongVideoBench?tab=readme-ov-file#custom-use-load-the-longvideobench-dataset).

   Use the following Python snippet to load the dataset in your scripts:
   ```python
   # Remember to use VideoAutoBench's src/load_longvideobench.py
   from longvideobench import LongVideoBenchDataset

   dataset = LongVideoBenchDataset(YOUR_DATA_PATH_TO_LVB, "lvb_test_wo_gt.json", max_num_frames=128)

   # Example of loading video contents
   video_id = "@jonijawne-7305429122044497157"
   video_contents = dataset.get_w_video_id(video_id)["inputs"]  # Returns a list of PIL.Images and subtitles
   ```

2. **Generate Model Responses**  
   Use `video_contents` along with the questions from `data/videoautobench.latest.json` to generate responses using your LMMs.  
   > **Note**: Do not include the "persona" information from the dataset in the input to your model.

3. **Format the Responses**  
   Once you have generated the answers, format them as follows:
   ```json
   {
       "@thatrecipe.us-7327402732199955755_3": {
           "video_id": "@thatrecipe.us-7327402732199955755",
           "qid": "@thatrecipe.us-7327402732199955755_3",
           "persona": "A person who is ...",
           "question": "As an office manager looking to impress your friends with a recipe during a weekend get-together, describe how ...",
           "response": "..."
       },
       ...
   }
   ```
   > **Example**: Refer to `example/responses/videoautobench.aria.json` for a complete sample.



### Step 2: Generate GPT-4o Judgments

In this step, GPT-4o evaluates your model’s responses by comparing them to human-selected or human-rejected answers.

1. **Set Up Environment**  
   Ensure your environment is ready:
   ```bash
   cd src
   export OPENAI_API_KEY=XXXXXX  # Replace with your OpenAI API key
   export LVB_PATH=YYYYYY # Replace with your path to the LongVideoBench"
   ```

2. **Run the Judging Script**  
   Use the `lmm_judge.py` script to start the evaluation process:
   ```bash
   python lmm_judge.py \
       --vab_path "/path/to/videoautobench.latest.json" \
       --ans_path "/path/to/your/model/answers.json" \
       --mode "selected" \  # or "rejected"
       --output_dir "/path/to/save/judge/results" \
       --worker_num 2  # Adjust based on your hardware capacity
   ```

   - **`vab_path`**: Path to the VideoAutoBench questions file.  
   - **`ans_path`**: Path to your model’s answers.  
   - **`mode`**: Determines comparison type:  
     - `"selected"`: Compare against human-selected responses.  
     - `"rejected"`: Compare against human-rejected responses.  
   - **`output_dir`**: Directory to save GPT-4o judgment results.  

   Example command:
   ```bash
   python lmm_judge.py \
       --vab_path "VideoAutoBench/data/videoautobench.latest.json" \
       --ans_path "VideoAutoBench/example/videoautobench.aria.json" \
       --mode "selected" \
       --output_dir "VideoAutoBench/output/videoautobench.aria.selected.judge"
   ```

> **Example**: Refer to `example/judges/videoautobench.aria.selected.judge.zip` and `example/judges/videoautobench.aria.rejected.judge.zip` for the complete samples.

### Step 3: Show VideoAutoBench Scores

Once GPT-4o judgments are generated, calculate the final scores for your model.

1. **Run the Scoring Script**  
   Use `get_score.py` to process the judgments and generate scores:
   ```bash
   python get_score.py \
       --vab_path "/path/to/videoautobench.latest.json" \
       --input_dir "/path/to/judge/results" \
       --mode "selected"  # or "rejected"
   ```

   - **`vab_path`**: Path to the VideoAutoBench questions file.  
   - **`input_dir`**: Directory containing GPT-4o judgment results.  
   - **`mode`**: Same as the one used during judgment (`selected` or `rejected`).  

   Example command:
   ```bash
   python get_score.py \
       --vab_path "VideoAutoBench/data/videoautobench.latest.json" \
       --input_dir "VideoAutoBench/output/videoautobench.aria.selected.judge" \
       --mode "selected"
   ```

2. **Interpret the Results**  
   The script will output your model’s score, which reflects its performance against human-selected or rejected responses.



## 📬 Contact

If you would like your LMM's performance included on our [leaderboard](https://videoautoarena.github.io/), please email your judge results to us (e.g. `videoautobench.aria.selected.judge.zip`). For any questions or further inquiries, contact us at `chiyeunglaw1@gmail.com`.


## 📜 License

This dataset follows the **CC-BY-NC-SA 4.0** license. Please use this dataset for **non-commercial purposes ONLY**.

For more information, see the [Creative Commons License](https://creativecommons.org/licenses/by-nc-sa/4.0/).



## 📖 Citation

If you find this project useful, please cite our work:

```bibtex
@article{
    luo2024videoautoarena,
    title={VideoAutoArena: An Automated Arena for Evaluating Large Multimodal Models in Video Analysis through User Simulation}, 
    author={Ziyang Luo and Haoning Wu and Dongxu Li and Jing Ma and Mohan Kankanhalli and Junnan Li},
    year={2024},
    eprint={2411.13281},
    archivePrefix={arXiv},
    primaryClass={cs.CV},
    url={https://arxiv.org/abs/2411.13281}, 
}
```
