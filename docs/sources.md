# Sources and verbatim quotes (generated from data/sources.yaml)

Every quote below is checked verbatim against the downloaded source by `verify_sources`
(and `uv run pytest -m network`). Quotes from non-CC-BY-4.0 sources are kept to at most 15 words.

## Turner et al. 2024, arXiv:2308.10248

Turner, A. M., Thiergart, L., Leech, G., Udell, D., Vazquez, J. J., Mini, U., MacDiarmid, M. (2024). Steering Language Models With Activation Engineering (v1-v4 titled 'Activation Addition: Steering Language Models Without Optimization'). arXiv:2308.10248v5.  
Link: https://arxiv.org/abs/2308.10248  
License: CC BY 4.0

- **actadd_definition** (Abstract): “we introduce activation engineering: the inference-time modification of activations in order to control (or steer) model outputs.”
- **actadd_single_pair** (Abstract): “it does not require any machine optimization and works with a single pair of data points”
- **actadd_bias_terms** (Section 1): “These vectors act like “virtual bias terms” because ActAdd directly adds the steering vectors to the forward pass at inference time.”
- **actadd_padding** (Appendix C): “The contrast pair can be of arbitrary lengths (empirically, right-padding the shorter prompt using whitespace gives good results).”
- **actadd_coeff_limit** (Appendix C): “The injection coefficient cannot be increased indefinitely, as shown by our coefficient sweeps (see Appendix Table 7).”
- **actadd_middle_layers** (Section 3, footnote 2): “intervening at the middle layers is most effective.”
- **actadd_api_access** (Section 5 (Limitations)): “ActAdd is not immediately applicable given only API access to a model.”

## Turner et al. 2023, LessWrong

Turner, A. M., Thiergart, L., Udell, D., Leech, G., Mini, U., MacDiarmid, M. (2023). Steering GPT-2-XL by adding an activation vector. LessWrong / AI Alignment Forum.  
Link: https://www.lesswrong.com/posts/5spBue2z2tw4JuDCx/steering-gpt-2-xl-by-adding-an-activation-vector  
License: all rights reserved (no license stated)

- **lw_love_hate_setup** (Section 'Demonstrations'): “"Love" - "Hate" before attention layer 6 with coefficient +5”
- **lw_cherry_picked** (Introduction): “We slightly (best-of-3) cherry-picked our results in order to make the post shorter.”

## montemac/activation_additions (MIT)

Turner, A. M., MacDiarmid, M., et al. activation_additions: code for ActAdd (GitHub repository, MIT license).  
Link: https://github.com/montemac/activation_additions  
License: MIT

- **code_sampling_kwargs** (README, 'Using ActivationAdditions to generate modified completions'): “temperature=1, freq_penalty=1, top_p=.3”
- **code_love_vector** (README): “love_rp = ActivationAddition(prompt="Love", coeff=5, act_name="blocks.6.hook_resid_pre")”

## Rimsky et al. 2024 (CAA), ACL

Rimsky (Panickssery), N., Gabrieli, N., Schulz, J., Tong, M., Hubinger, E., Turner, A. M. (2024). Steering Llama 2 via Contrastive Activation Addition. Proceedings of ACL 2024 (Long Papers), 15504-15522. arXiv:2312.06681.  
Link: https://aclanthology.org/2024.acl-long.828/  
License: CC BY 4.0

- **caa_definition** (Abstract): “CAA computes “steering vectors” by averaging the difference in residual stream activations between pairs of positive and negative examples of a particular behavior, such as factual versus hallucinatory responses.”
- **caa_positions** (Abstract): “these steering vectors are added at all token positions after the user’s prompt”

## Subramani et al. 2022, Findings of ACL

Subramani, N., Suresh, N., Peters, M. E. (2022). Extracting Latent Steering Vectors from Pretrained Language Models. Findings of ACL 2022, 566-581. arXiv:2205.05124.  
Link: https://aclanthology.org/2022.findings-acl.48/  
License: CC BY 4.0

- **subramani_add** (Section 1): “During decoding, we add our steering vector to the hidden states of the language model to generate the target sentence.”

## Mikolov et al. 2013, NAACL

Mikolov, T., Yih, W., Zweig, G. (2013). Linguistic Regularities in Continuous Space Word Representations. Proceedings of NAACL-HLT 2013, 746-751.  
Link: https://aclanthology.org/N13-1090/  
License: ACL Anthology (pre-2016, no CC license)

- **mikolov_king_queen** (Abstract, p. 746): “"King - Man + Woman" results in a vector very close to "Queen."”

## Park et al. 2024, ICML

Park, K., Choe, Y. J., Veitch, V. (2024). The Linear Representation Hypothesis and the Geometry of Large Language Models. ICML 2024. arXiv:2311.03658.  
Link: https://arxiv.org/abs/2311.03658  
License: CC BY-NC-SA 4.0

- **park_lrh** (Abstract): “high-level concepts are represented linearly as directions in some representation space”

## Elhage et al. 2021, Transformer Circuits

Elhage, N., Nanda, N., Olsson, C., et al. (2021). A Mathematical Framework for Transformer Circuits. Transformer Circuits Thread.  
Link: https://transformer-circuits.pub/2021/framework/index.html  
License: no license stated

- **elhage_residual_sum** (Section 'Virtual Weights and the Residual Stream as a Communication Channel'): “simply the sum of the output of all the previous layers and the original embedding”

## Radford et al. 2019 (GPT-2)

Radford, A., Wu, J., Child, R., Luan, D., Amodei, D., Sutskever, I. (2019). Language Models are Unsupervised Multitask Learners. OpenAI technical report.  
Link: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf  
License: no license stated

- **gpt2_vocab** (Section 2.3): “The vocabulary is expanded to 50,257.”

## Arditi et al. 2024, NeurIPS

Arditi, A., Obeso, O., Syed, A., Paleka, D., Panickssery, N., Gurnee, W., Nanda, N. (2024). Refusal in Language Models Is Mediated by a Single Direction. NeurIPS 2024. arXiv:2406.11717.  
Link: https://arxiv.org/abs/2406.11717  
License: arXiv non-exclusive

- **arditi_one_dim** (Abstract): “refusal is mediated by a one-dimensional subspace”

## Tan et al. 2024, NeurIPS

Tan, D., Chanin, D., Lynch, A., Kanoulas, D., Paige, B., Garriga-Alonso, A., Kirk, R. (2024). Analyzing the Generalization and Reliability of Steering Vectors. NeurIPS 2024. arXiv:2407.12404.  
Link: https://arxiv.org/abs/2407.12404  
License: CC BY 4.0

- **tan_variable** (Abstract): “In-distribution, steerability is highly variable across different inputs.”
- **tan_anti_steerable** (Section 5 (Evaluating Steering Vector Reliability)): “Many of these datasets have almost half of the inputs being anti-steerable, implying that the effect of steering is highly unreliable.”

## Li et al. 2023 (ITI), NeurIPS

Li, K., Patel, O., Viegas, F., Pfister, H., Wattenberg, M. (2023). Inference-Time Intervention: Eliciting Truthful Answers from a Language Model. NeurIPS 2023. arXiv:2306.03341.  
Link: https://arxiv.org/abs/2306.03341  
License: CC BY 4.0

- **iti_definition** (Abstract): “ITI operates by shifting model activations during inference, following a set of directions across a limited number of attention heads.”

## Zou et al. 2023 (RepE)

Zou, A., Phan, L., Chen, S., et al. (2023). Representation Engineering: A Top-Down Approach to AI Transparency. arXiv:2310.01405.  
Link: https://arxiv.org/abs/2310.01405  
License: arXiv non-exclusive

- **repe_definition** (Figure 1 caption): “a top-down approach to AI transparency called representation engineering (RepE)”

## Templeton et al. 2024, Transformer Circuits

Templeton, A., Conerly, T., Marcus, J., et al. (2024). Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet. Transformer Circuits Thread.  
Link: https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html  
License: no license stated

- **templeton_clamp** (Section 'Feature steering'): “"clamp" specific features of interest to artificially high or low values during the forward pass”

## Anthropic 2024, Golden Gate Claude

Anthropic (2024, May 23). Golden Gate Claude. anthropic.com/news.  
Link: https://www.anthropic.com/news/golden-gate-claude  
License: no license stated

- **goldengate_surgical** (Body): “surgical change to some of the most basic aspects of the model's internal activations”

## Chen et al. 2025 (Persona Vectors)

Chen, R., Arditi, A., Sleight, H., Evans, O., Lindsey, J. (2025). Persona Vectors: Monitoring and Controlling Character Traits in Language Models. arXiv:2507.21509.  
Link: https://arxiv.org/abs/2507.21509  
License: arXiv non-exclusive

- **persona_mean_diff** (Abstract): “computed as the difference in mean activations between responses exhibiting the target trait”

## Vaswani et al. 2017, NeurIPS

Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention Is All You Need. NeurIPS 2017. arXiv:1706.03762.  
Link: https://arxiv.org/abs/1706.03762  
License: arXiv non-exclusive


## Maas et al. 2011 (IMDb)

Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., Potts, C. (2011). Learning Word Vectors for Sentiment Analysis. ACL 2011, 142-150.  
Link: https://aclanthology.org/P11-1015/  
License: citation only


## Hartmann et al. 2023 (SiEBERT)

Hartmann, J., Heitmann, M., Siebert, C., Schamp, C. (2023). More than a Feeling: Accuracy and Application of Sentiment Analysis. International Journal of Research in Marketing 40(1), 75-87.  
Link: https://huggingface.co/siebert/sentiment-roberta-large-english  
License: citation only


## Holm 1979

Holm, S. (1979). A Simple Sequentially Rejective Multiple Test Procedure. Scandinavian Journal of Statistics 6(2), 65-70.  
Link: https://www.jstor.org/stable/4615733  
License: citation only


## Lones 2021

Lones, M. A. (2021). How to avoid machine learning pitfalls: a guide for academic researchers. arXiv:2108.02497.  
Link: https://arxiv.org/abs/2108.02497  
License: citation only


## Nosek et al. 2018

Nosek, B. A., Ebersole, C. R., DeHaven, A. C., Mellor, D. T. (2018). The preregistration revolution. PNAS 115(11), 2600-2606.  
Link: https://doi.org/10.1073/pnas.1708274114  
License: citation only


## Efron & Tibshirani 1993

Efron, B., Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall/CRC.  
Link: https://doi.org/10.1201/9780429246593  
License: citation only

