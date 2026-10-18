# Steering vectors, from scratch — video description

Narrated explainer of LLM steering vectors (activation addition), every term defined from scratch,
grounded in a real, pre-registered GPT-2-XL experiment. Author: Libor Burian (independent researcher).
Code, data and logs: https://github.com/BurnyCoder/steering-vectors-explained

## Chapters

00:00 Steering vectors, from scratch
00:42 1 · Numbers and vectors
01:36 2 · Vector arithmetic
02:50 3 · From text to vectors
03:50 4 · Layers and the residual stream
05:08 5 · From vectors back to words
06:01 6 · Concepts as directions
06:44 7 · Building the steering vector
08:30 8 · Steering: adding the vector
09:49 9 · Does it really work?
11:36 10 · Nuances and relatives
12:35 11 · Recap

Total length: 13:12

## Sources

- Turner, A. M., Thiergart, L., Leech, G., Udell, D., Vazquez, J. J., Mini, U., MacDiarmid, M. (2024). Steering Language Models With Activation Engineering (v1-v4 titled 'Activation Addition: Steering Language Models Without Optimization'). arXiv:2308.10248v5. https://arxiv.org/abs/2308.10248
- Turner, A. M., Thiergart, L., Udell, D., Leech, G., Mini, U., MacDiarmid, M. (2023). Steering GPT-2-XL by adding an activation vector. LessWrong / AI Alignment Forum. https://www.lesswrong.com/posts/5spBue2z2tw4JuDCx/steering-gpt-2-xl-by-adding-an-activation-vector
- Turner, A. M., MacDiarmid, M., et al. activation_additions: code for ActAdd (GitHub repository, MIT license). https://github.com/montemac/activation_additions
- Rimsky (Panickssery), N., Gabrieli, N., Schulz, J., Tong, M., Hubinger, E., Turner, A. M. (2024). Steering Llama 2 via Contrastive Activation Addition. Proceedings of ACL 2024 (Long Papers), 15504-15522. arXiv:2312.06681. https://aclanthology.org/2024.acl-long.828/
- Subramani, N., Suresh, N., Peters, M. E. (2022). Extracting Latent Steering Vectors from Pretrained Language Models. Findings of ACL 2022, 566-581. arXiv:2205.05124. https://aclanthology.org/2022.findings-acl.48/
- Mikolov, T., Yih, W., Zweig, G. (2013). Linguistic Regularities in Continuous Space Word Representations. Proceedings of NAACL-HLT 2013, 746-751. https://aclanthology.org/N13-1090/
- Park, K., Choe, Y. J., Veitch, V. (2024). The Linear Representation Hypothesis and the Geometry of Large Language Models. ICML 2024. arXiv:2311.03658. https://arxiv.org/abs/2311.03658
- Elhage, N., Nanda, N., Olsson, C., et al. (2021). A Mathematical Framework for Transformer Circuits. Transformer Circuits Thread. https://transformer-circuits.pub/2021/framework/index.html
- Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., Sutskever, I. (2019). Language Models are Unsupervised Multitask Learners. OpenAI technical report. https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
- Arditi, A., Obeso, O., Syed, A., Paleka, D., Panickssery, N., Gurnee, W., Nanda, N. (2024). Refusal in Language Models Is Mediated by a Single Direction. NeurIPS 2024. arXiv:2406.11717. https://arxiv.org/abs/2406.11717
- Tan, D., Chanin, D., Lynch, A., Kanoulas, D., Paige, B., Garriga-Alonso, A., Kirk, R. (2024). Analyzing the Generalization and Reliability of Steering Vectors. NeurIPS 2024. arXiv:2407.12404. https://arxiv.org/abs/2407.12404
- Li, K., Patel, O., Viegas, F., Pfister, H., Wattenberg, M. (2023). Inference-Time Intervention: Eliciting Truthful Answers from a Language Model. NeurIPS 2023. arXiv:2306.03341. https://arxiv.org/abs/2306.03341
- Zou, A., Phan, L., Chen, S., et al. (2023). Representation Engineering: A Top-Down Approach to AI Transparency. arXiv:2310.01405. https://arxiv.org/abs/2310.01405
- Templeton, A., Conerly, T., Marcus, J., et al. (2024). Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet. Transformer Circuits Thread. https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html
- Anthropic (2024, May 23). Golden Gate Claude. anthropic.com/news. https://www.anthropic.com/news/golden-gate-claude
- Chen, R., Arditi, A., Sleight, H., Evans, O., Lindsey, J. (2025). Persona Vectors: Monitoring and Controlling Character Traits in Language Models. arXiv:2507.21509. https://arxiv.org/abs/2507.21509
- Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention Is All You Need. NeurIPS 2017. arXiv:1706.03762. https://arxiv.org/abs/1706.03762
- Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., Potts, C. (2011). Learning Word Vectors for Sentiment Analysis. ACL 2011, 142-150. https://aclanthology.org/P11-1015/
- Hartmann, J., Heitmann, M., Siebert, C., Schamp, C. (2023). More than a Feeling: Accuracy and Application of Sentiment Analysis. International Journal of Research in Marketing 40(1), 75-87. https://huggingface.co/siebert/sentiment-roberta-large-english
- Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. Scandinavian Journal of Statistics 6(2), 65-70. https://www.jstor.org/stable/4615733
- Lones, M. A. (2021). How to avoid machine learning pitfalls: a guide for academic researchers. arXiv:2108.02497. https://arxiv.org/abs/2108.02497
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. (2018). The preregistration revolution. PNAS 115(11), 2600-2606. https://doi.org/10.1073/pnas.1708274114
- Efron, B., Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall/CRC. https://doi.org/10.1201/9780429246593
