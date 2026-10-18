# Fact-check of the video (v1.0 → v1.1)

Every claim in the v1.0 video was checked independently, and the errors were fixed for v1.1. "Claims" means the narration
(`data/script.yaml` plus the sentences that `video/narration_values.py` generates), everything on screen
(`video/scenes/*.py`, `video/formulas.py`), the citations (`data/sources.yaml`) and the generated description.

**How it was checked.** Three separate audits:
1. An inventory of every on-screen string, formula and footer, compared with the narration and the JSON data.
2. Every citation and quote compared with its primary source online: authors, venue, pages, license, verbatim text,
   location, and whether the context supports how the video uses it.
3. A re-derivation of every code and data claim:
   * GPT-2-XL re-run: seed 0 reproduces `data/practical_example.json` exactly; float16 vs float32 differ by ≤ 0.01;
   * all statistics recomputed from `data/study/*.jsonl`; they match the summary JSONs exactly;
   * git and GitHub push times of the pre-registrations compared with the data commits.

Quotes are re-checked automatically by `uv run pytest -m network`, which downloads every source.

## Errors found and how they were fixed

| # | Where (v1.0) | Claim | What was wrong | Fix in v1.1 | Evidence |
|---|---|---|---|---|---|
| 1 | ch00, ch08, ch09 screen | "same random choices" | Steered and unsteered texts are rows of one sampled batch. `torch.multinomial` draws separate random numbers for each row. Two α = 0 rows with the same seed already differ. | "same random seed" / "same seeds"; glossary term *random seed* | `steering/intervene.py` `sample`; [torch.multinomial](https://pytorch.org/docs/stable/generated/torch.multinomial.html) |
| 2 | ch03 | "GPT-2 also starts every text with a special end-of-text token" | GPT-2's tokenizer adds nothing. TransformerLens prepends `<\|endoftext\|>` by default, and the ActAdd code used it. | "Like the library the original experiment used, we start every text with … ; GPT-2's own tokenizer does not add it" + TransformerLens quote card | `tl_gpt2_no_bos`, `tl_prepend_default`, `hf_no_bos` in [sources](sources.md) |
| 3 | ch07 `formula` | "ActAdd is the case where D holds one pair" | ActAdd has no completions, reads every position (h_A ∈ ℝ^{n×d}) and adds a different vector at each front position. The caption was also on screen for ~1 s, late. | "ActAdd is like the case … but it has no completions and keeps one difference per position"; caption synced to a bookmark. ch08: "row t of h_A at each front position"; ch11 row "(ActAdd: one per position)". | Turner et al. 2024 §3; Rimsky et al. 2024 Eq. 1 |
| 4 | ch07 `real` | "the Love and Hate activations have norms of about 98 and 97 … difference has norm 73.8" | These are values at position 1 only, where "Hate" is the token "H". The norm of the whole 3×1600 difference is ≈ 107.6. The narration said "97", the screen "97.5". | Narration and screen say position 1 and "H"; both use one decimal. | `steering/example.py` |
| 5 | ch09 `question` | "Each opening was continued under six values of alpha, three times each" | It omitted 30 of the 48 continuations per prompt: 5 random directions × α ∈ {5, 15} × 3 seeds. | Sentence and screen computed from the summary: "48 continuations: three at each of six values of alpha, and three for each of five random directions at alpha 5 and 15" | `study/design.py`, `n_completions / n_prompts` |
| 6 | ch09 post-hoc | "29% of continuations contain the word hate" | The substring pattern `hat(e\|ing\|red)` also matched "whatever", "chateau" and glued text. | Whole-word patterns (`study/posthoc.py`, tested in `tests/test_posthoc.py`): "hate" at α = −5 is 22.5% (was 29.5%); "love" at α = +5 is 61.4% (was 62.5%). | `data/study/exp02_posthoc.json` |
| 7 | ch09 post-hoc | "A check … hints at why" | Nothing in v1.0 linked the check to the missing negativity. | The new number shows it. The 128 α = −5 continuations that contain "hate" average P(positive) 0.665, the same as unsteered text (0.665). Narration: "suggests the vector inserts the words more than the sentiment". | `exp02_posthoc.json` |
| 8 | ch05 `sampling` | "picks the next token at random with those probabilities" | Every completion shown used top-p 0.3 and frequency penalty 1, which change the distribution. This was never said. | Narration plus a settings line and the ActAdd code quote `code_sampling_kwargs` | `.env.example`; montemac/activation_additions README |
| 9 | ch05 `logits`, ch00 context line | z = W_U h_L | GPT-2 normalizes the final stream (`ln_f`) before the unembedding. | z = W_U LN(h_L); "after one last normalization"; quotes `gpt2_final_ln`, `hf_final_ln` | Radford et al. 2019 §2.3; HF `modeling_gpt2.py` |
| 10 | ch04 `parts` | attention reads "earlier positions" | Causal attention also reads the current position. | "itself and earlier positions" + quote `vaswani_causal` | Vaswani et al. 2017 §3.2.3 |
| 11 | ch04 `residual` | "Leaving out … normalization, h_{ℓ+1} = …" | GPT-2 is pre-LayerNorm, so the residual sum is exact. Normalization only rescales what each sub-layer reads. | "Each part first rescales what it reads … but its output is simply added"; quote `gpt2_preln` | Radford et al. 2019 §2.3 |
| 12 | ch03 `embedding` | "a function from tokens to vectors" | The position is an input too (learned `wpe`). The screen also reused `e` (Euler's number). | "a function from a token and its position"; Embed: V×{0,1,…}→ℝ^d with e_tok, e_pos | HF `modeling_gpt2.py` (`hf_learned_positions`) |
| 13 | ch07 `dataset` | "One pair is noisy"; activations at "the completion's last token" | The first claim had no source. CAA reads the answer-letter position, which is index −2 in its code because of the closing parenthesis. | Quote `caa_noise`; "at the position of c's answer letter" (ch07, ch11) | Rimsky et al. 2024 §2, §3 (`caa_answer_letter`) |
| 14 | ch10 `limits` | "Middle layers tend to work best" | This clashed with the video's own layer 6 of 48. ActAdd's GPT-2-XL evidence favours layer 6 for Love and 23 for Conspiracy. | "Middle layers are often most effective, but it depends on the concept …" + quote `actadd_layer_choice` | Turner et al. 2024 §3, App. C |
| 15 | ch10 RepE | "reads and controls such directions" | The quote shown ("a top-down approach…") does not say that. | Quote `repe_reading_control` | Zou et al. 2023 §1 |
| 16 | ch09 `result` | "positivity peaked at alpha 10 and fell back at 15" | This read like a tested claim, but α = 10 vs 5 is not significant. The pre-registered dose–response test (H2) was never reported. | "average positivity was highest at alpha 10 and lower again at 15" (descriptive) + "Our planned test of a steady rise with alpha failed in the first run and held in the second" | `summary.json`, `exp02_summary.json` `h2_spearman` |
| 17 | ch09 `question` | "before collecting any data" | Exp02's plan was written after seeing exp01's data. | "each run's hypotheses and analysis before collecting its data" | pre-registration commits `7da591f`, `23a32f4` |
| 18 | ch09 `metric`, `cost` | "scored … from zero to one"; NLL "per token … less natural" | SiEBERT is binary, so its score is P(positive). The NLL had no unit, and "less natural" overclaims. | "the probability … that it is positive"; "in nats per token … a rough sign of less fluent text"; glossary term *nats* | `study/score.py`, `steering/intervene.py` |
| 19 | ch01 | spoken "1.6 billion", shown "1.56"; footer "read from the config" | The count is a sum over weight tensors: 1,557,611,200. The GPT-2 paper's Table 2 lists 1542M. | Spoken "1.56"; footer says how it was counted | `steering/example.py` |
| 20 | ch06 | King − Man + Woman ≈ Queen | Common analogy implementations exclude the input words from the search. | Quote `nissim_ignore_inputs`; "fails for others" now cites Engels et al. 2024 (circular features) | Nissim et al. 2020 §3–4.1; Engels et al. 2024 |
| 21 | ch08 `toy` | toy logits | W_U was applied directly to h̃, skipping the later layers, and the W_U rows were not on screen. | "treating h as the final stream"; W_U rows shown | `video/toy.py` |
| 22 | sources | LessWrong post authors | Gavin Leech is not an author of the post. The author order was also wrong. | Turner, MacDiarmid, Udell, Thiergart, Mini (13 May 2023) | LessWrong post byline |
| 23 | sources | quote locations | Four locations were wrong: `actadd_middle_layers` (main text, not a footnote), `lw_cherry_picked` (Demonstrations section), `templeton_clamp` ("Influence on Behavior"), `persona_mean_diff` (Figure 2 caption). | Corrected | primary sources |
| 24 | sources | licenses / bibliographic details | Five details were wrong: the Mikolov 2013 license (CC BY-NC-SA 3.0), Tan et al.'s NeurIPS title and author order, the accent in Viégas, the ActAdd code authors, and the SiEBERT link (model card, not the paper DOI). | Corrected | ACL Anthology, NeurIPS, GitHub, DOI |
| 25 | description | "Code, data and logs" | `logs/` is gitignored, so the logs are not in the repository. | "Code and data", plus a link to this file | `.gitignore` |

## Checked and correct (unchanged)
* **Numbers.** Every spoken and displayed number matches its JSON source. The toy arithmetic is pinned by `tests/test_toy.py`.
* **Steering hook.** It matches ActAdd's original code: it adds to the input of block 6 at the front positions,
  edits the prompt only, and skips cached one-token steps.
* **Padding.** Padding "Love" with a space matches the LessWrong post (footnote 6) and the paper (App. C).
* **Prompts.** The prompts are disjoint IMDb test openings (pilot 0–19, exp01 20–49, exp02 50–239).
* **Sample size.** N = 190 follows from exp01's d_z = 0.205 (80% power).
* **Pre-registration order.** Each pre-registration was pushed before its run started.
* **Steered vs random.** steered(5) − random(5) holds in both runs: +0.125 [+0.045, +0.203] and +0.132 [+0.097, +0.166].
* **Quotes.** All quotes are verbatim.

## Learnings
* **Batched sampling.** It does not give paired random draws. "Same seed" is the accurate claim. Sharing the
  uniform draws across rows (common random numbers) would make "same random choices" true, but that would mean
  changing the sampler and re-running the study.
* **Substring regexes.** They overcount words: "hate" is a substring of "whatever". Use word boundaries and test
  the negatives.
* **Library defaults.** A default such as TransformerLens' `prepend_bos` is easy to mistake for model behaviour.
  Attribute it to the library that sets it.
* **Paraphrases.** A paraphrase can drift from the quote shown beside it (RepE, Tan "in-distribution"). Check that
  each on-screen quote supports the exact spoken sentence.
* **Selective reporting.** Even an honest sentence template can report selectively: H2 was pre-registered but
  never spoken. Every pre-registered hypothesis should be voiced.
