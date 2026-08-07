# AI and Tool Usage

| Tool or source | What I used it for | What I checked or changed |
|---|---|---|
| ChatGPT | I used ChatGPT to help interpret the assignment requirements, draft and review implementations for the starter TODOs, troubleshoot the training workflow, and review the report. | I inspected the proposed implementation choices, ran the tests and all reported experiments myself, checked the generated metrics and files, and made the final decisions about which methods and results to retain. |
| PyTorch and torchvision documentation, and the original ResNet paper | I used these sources to check the ResNet18 architecture, torchvision pretrained-weight interface, ImageNet normalization, and the behavior of the loss and optimizer used in the project. | I compared the implementation against the requirements at the top of the starter files, verified that both models output four logits, and checked that the required baseline and transfer configurations used the intended architecture and preprocessing. |

One useful suggestion from ChatGPT was to save an independent `best_<run_id>.pt` checkpoint for every run instead of allowing successive experiments to overwrite the same checkpoint. I accepted this suggestion because it kept the baseline, transfer, and ablation results separate and allowed each recorded experiment to be evaluated again with its own best-validation-macro-F1 checkpoint.

One suggestion from ChatGPT that I rejected was to compare different optimizers as an ablation and support several optimizer choices in the training code. I decided that a fair Adam-versus-SGD comparison would require separate learning-rate and schedule tuning, so changing only the optimizer under one shared configuration could be misleading. I therefore kept AdamW as the single optimizer and used the compute budget for better-controlled ablations of learning rate, batch size, weight decay, and backbone freezing.
