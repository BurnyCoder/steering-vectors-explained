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
- **actadd_middle_layers** (Section 3 (main text)): “intervening at the middle layers is most effective.”
- **actadd_layer_choice** (Appendix C): “the Love vector is most effective inserted at layer 6, while the more abstract Conspiracy vector is better inserted later, at layer 23.”
- **actadd_api_access** (Section 5 (Limitations)): “ActAdd is not immediately applicable given only API access to a model.”

## Turner et al. 2023, LessWrong

Turner, A. M., MacDiarmid, M., Udell, D., Thiergart, L., Mini, U. (2023, May 13). Steering GPT-2-XL by adding an activation vector. LessWrong / AI Alignment Forum.  
Link: https://www.lesswrong.com/posts/5spBue2z2tw4JuDCx/steering-gpt-2-xl-by-adding-an-activation-vector  
License: all rights reserved (no license stated)

- **lw_love_hate_setup** (Section 'Demonstrations', example 1): ““Love”—“Hate” before attention layer 6 with coefficient +5”
- **lw_cherry_picked** (Section 'Demonstrations' (the introduction's example was best-of-30, footnote 1)): “We slightly (best-of-3) cherry-picked our results in order to make the post shorter.”

## montemac/activation_additions (MIT)

MacDiarmid, M., Udell, D., Mini, U., Thiergart, L., et al. (2023). activation_additions: 'Algebraic value editing in pretrained language models', the ActAdd code (GitHub repository, MIT license).  
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
- **caa_noise** (Section 2 (Related work)): “Using hundreds of diverse contrast pairs reduces noise in the steering vector, allowing for a more precise encoding of the behavior of interest.”
- **caa_answer_letter** (Section 3 (Method)): “we compute the difference in the language model's activations at the position of the answer letter between all the positive and negative prompts”

## Subramani et al. 2022, Findings of ACL

Subramani, N., Suresh, N., Peters, M. E. (2022). Extracting Latent Steering Vectors from Pretrained Language Models. Findings of ACL 2022, 566-581. arXiv:2205.05124.  
Link: https://aclanthology.org/2022.findings-acl.48/  
License: CC BY 4.0

- **subramani_add** (Section 1): “During decoding, we add our steering vector to the hidden states of the language model to generate the target sentence.”

## Mikolov et al. 2013, NAACL

Mikolov, T., Yih, W., Zweig, G. (2013). Linguistic Regularities in Continuous Space Word Representations. Proceedings of NAACL-HLT 2013, 746-751.  
Link: https://aclanthology.org/N13-1090/  
License: CC BY-NC-SA 3.0 (ACL Anthology, pre-2016 papers)

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
- **gpt2_preln** (Section 2.3): “Layer normalization (Ba et al., 2016) was moved to the input of each sub-block”
- **gpt2_final_ln** (Section 2.3): “an additional layer normalization was added after the final self-attention block”

## Arditi et al. 2024, NeurIPS

Arditi, A., Obeso, O., Syed, A., Paleka, D., Panickssery, N., Gurnee, W., Nanda, N. (2024). Refusal in Language Models Is Mediated by a Single Direction. NeurIPS 2024. arXiv:2406.11717.  
Link: https://arxiv.org/abs/2406.11717  
License: arXiv non-exclusive

- **arditi_one_dim** (Abstract): “refusal is mediated by a one-dimensional subspace”

## Tan et al. 2024, NeurIPS

Tan, D., Chanin, D., Lynch, A., Paige, B., Kanoulas, D., Garriga-Alonso, A., Kirk, R. (2024). Analysing the Generalisation and Reliability of Steering Vectors. NeurIPS 2024. arXiv:2407.12404 (arXiv listing titled 'Analyzing the Generalization ...').  
Link: https://arxiv.org/abs/2407.12404  
License: CC BY 4.0

- **tan_variable** (Abstract): “In-distribution, steerability is highly variable across different inputs.”
- **tan_anti_steerable** (Section 5 (Evaluating Steering Vector Reliability)): “Many of these datasets have almost half of the inputs being anti-steerable, implying that the effect of steering is highly unreliable.”

## Li et al. 2023 (ITI), NeurIPS

Li, K., Patel, O., Viégas, F., Pfister, H., Wattenberg, M. (2023). Inference-Time Intervention: Eliciting Truthful Answers from a Language Model. NeurIPS 2023. arXiv:2306.03341.  
Link: https://arxiv.org/abs/2306.03341  
License: CC BY 4.0

- **iti_definition** (Abstract): “ITI operates by shifting model activations during inference, following a set of directions across a limited number of attention heads.”

## Zou et al. 2023 (RepE)

Zou, A., Phan, L., Chen, S., et al. (2023). Representation Engineering: A Top-Down Approach to AI Transparency. arXiv:2310.01405.  
Link: https://arxiv.org/abs/2310.01405  
License: arXiv non-exclusive

- **repe_definition** (Figure 1 caption): “a top-down approach to AI transparency called representation engineering (RepE)”
- **repe_reading_control** (Section 1 (Introduction)): “we develop improved baselines for reading and controlling representations”

## Templeton et al. 2024, Transformer Circuits

Templeton, A., Conerly, T., Marcus, J., et al. (2024). Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet. Transformer Circuits Thread.  
Link: https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html  
License: no license stated

- **templeton_clamp** (Section 'Assessing Feature Interpretability', subsection 'Influence on Behavior'): “"clamp" specific features of interest to artificially high or low values during the forward pass”

## Anthropic 2024, Golden Gate Claude

Anthropic (2024, May 23). Golden Gate Claude. anthropic.com/news.  
Link: https://www.anthropic.com/news/golden-gate-claude  
License: no license stated

- **goldengate_surgical** (Body): “surgical change to some of the most basic aspects of the model's internal activations”

## Chen et al. 2025 (Persona Vectors)

Chen, R., Arditi, A., Sleight, H., Evans, O., Lindsey, J. (2025). Persona Vectors: Monitoring and Controlling Character Traits in Language Models. arXiv:2507.21509.  
Link: https://arxiv.org/abs/2507.21509  
License: arXiv non-exclusive

- **persona_mean_diff** (Figure 2 caption (Section 2)): “computed as the difference in mean activations between responses exhibiting the target trait”

## TransformerLens (Nanda & Bloom 2022)

Nanda, N., Bloom, J. (2022). TransformerLens. GitHub repository (MIT license); quoted from transformer_lens/HookedTransformer.py at tag v2.15.4.  
Link: https://github.com/TransformerLensOrg/TransformerLens  
License: MIT

- **tl_prepend_default** (HookedTransformer.to_str_tokens docstring (default_prepend_bos)): “which is set to True unless specified otherwise”
- **tl_gpt2_no_bos** (HookedTransformer.to_str_tokens docstring): “some models eg GPT-2 were not trained with a BOS token”

## HF Transformers (Wolf et al. 2020), tokenization_gpt2.py

Wolf, T., Debut, L., Sanh, V., et al. (2020). Transformers: State-of-the-Art Natural Language Processing. Proceedings of EMNLP 2020: System Demonstrations, 38-45. Quoted from src/transformers/models/gpt2/tokenization_gpt2.py at tag v5.20.1 (Apache-2.0).  
Link: https://github.com/huggingface/transformers/blob/v5.20.1/src/transformers/models/gpt2/tokenization_gpt2.py  
License: Apache-2.0

- **hf_no_bos** (GPT2Tokenizer docstring): “add_bos_token (`bool`, *optional*, defaults to `False`)”

## HF Transformers (Wolf et al. 2020), modeling_gpt2.py

Wolf, T., Debut, L., Sanh, V., et al. (2020). Transformers: State-of-the-Art Natural Language Processing. Proceedings of EMNLP 2020: System Demonstrations, 38-45. Quoted from src/transformers/models/gpt2/modeling_gpt2.py at tag v5.20.1 (Apache-2.0).  
Link: https://github.com/huggingface/transformers/blob/v5.20.1/src/transformers/models/gpt2/modeling_gpt2.py  
License: Apache-2.0

- **hf_learned_positions** (GPT2Model.__init__ (learned position embeddings)): “self.wpe = nn.Embedding(config.max_position_embeddings, self.embed_dim)”
- **hf_final_ln** (GPT2Model.forward (final LayerNorm before the LM head)): “hidden_states = self.ln_f(hidden_states)”

## Nissim et al. 2020, Computational Linguistics

Nissim, M., van Noord, R., van der Goot, R. (2020). Fair Is Better than Sensational: Man Is to Doctor as Woman Is to Doctor. Computational Linguistics 46(2), 487-497. doi:10.1162/coli_a_00379.  
Link: https://aclanthology.org/2020.cl-2.7/  
License: CC BY 4.0

- **nissim_ignore_inputs** (Section 3): “in practice most implementations of these optimization functions specifically ignore one or more input vectors”

## Engels et al. 2024, ICLR 2025

Engels, J., Michaud, E. J., Liao, I., Gurnee, W., Tegmark, M. (2024). Not All Language Model Features Are One-Dimensionally Linear. ICLR 2025. arXiv:2405.14860.  
Link: https://arxiv.org/abs/2405.14860  
License: CC BY 4.0

- **engels_circular** (Abstract): “circular features representing days of the week and months of the year”

## Vaswani et al. 2017, NeurIPS

Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention Is All You Need. NeurIPS 2017. arXiv:1706.03762.  
Link: https://arxiv.org/abs/1706.03762  
License: arXiv non-exclusive

- **vaswani_causal** (Section 3.2.3): “attend to all positions in the decoder up to and including that position”

## Maas et al. 2011 (IMDb)

Maas, A. L., Daly, R. E., Pham, P. T., Huang, D., Ng, A. Y., Potts, C. (2011). Learning Word Vectors for Sentiment Analysis. ACL 2011, 142-150.  
Link: https://aclanthology.org/P11-1015/  
License: citation only


## Hartmann et al. 2023 (SiEBERT)

Hartmann, J., Heitmann, M., Siebert, C., Schamp, C. (2023). More than a Feeling: Accuracy and Application of Sentiment Analysis. International Journal of Research in Marketing 40(1), 75-87. Model: https://huggingface.co/siebert/sentiment-roberta-large-english  
Link: https://doi.org/10.1016/j.ijresmar.2022.05.005  
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

Efron, B., Tibshirani, R. J. (1993). An Introduction to the Bootstrap. Chapman & Hall (the Taylor & Francis DOI record lists 1994).  
Link: https://doi.org/10.1201/9780429246593  
License: citation only

