# Module 7 multiple-choice questions, draft

Written for the course author. This is a draft. It is not exported and not shown on the site.

There is one question for each step of module 7. Each question has three options and one correct answer. Every option has its own feedback. The feedback on a wrong option names the mistake in reasoning, so a student learns from a wrong choice. The correct option is in a different place in different questions.

The numbers come from the expected results of the steps in the 2026.4 export: lambda about 1.016 (main analysis) and about 1.546 (QC, no PCs), 236,815 finite tests, a Bonferroni threshold of about 2.11e-7, eight variants below 5e-8 in three regions on chromosomes 3, 9 and 12.

## Proposal for the site

- Keep the open quick check of each step. Add the multiple-choice question under it. The open question asks the student to reason. The multiple-choice question checks the reasoning.
- Store the question in the step JSON, in a new field, for example:

```json
"quiz": {
  "question": "...",
  "options": [
    { "text": "...", "correct": false, "feedback": "..." },
    { "text": "...", "correct": true, "feedback": "..." }
  ]
}
```

- Export it with release 2026.5. The site shows the question, lets the student choose, and then shows the feedback of the chosen option. It works with the keyboard. Without JavaScript, all options and their feedback stay readable.

## Questions

### 7.1 QQ plot

In the main analysis, most points lie on the diagonal. Only the highest points at the right end leave the line by a wide margin. What is the best reading?

- A. Something went wrong, because all points should lie on the line.
  - Feedback: The line shows what we expect if no variant is associated. Real signals are meant to leave it.
- B. A few true signals stand out, and there is little sign of inflation across the genome. (correct)
  - Feedback: Yes. Most tests behave as expected under no association. A few tests do not.
- C. The scan is confounded across the whole genome.
  - Feedback: Confounding across the genome lifts most of the points, not only the highest ones. Here the body of the plot stays on the line.

### 7.2 Genomic inflation factor

Lambda is about 1.016. What does this tell us?

- A. The test statistics as a whole are close to what we expect with no confounding. (correct)
  - Feedback: Yes. A value near 1 means little inflation across the genome. Each hit still needs its own checks.
- B. The top variants are causal.
  - Feedback: Lambda summarises the middle of all the tests. It says nothing about one single variant.
- C. About 1.6% of the hits are false positives.
  - Feedback: Lambda is not an error rate. It is the ratio of the median test statistic to the value we expect under no association.

### 7.3 Manhattan plot

Eight variants are below 5e-8, in three regions on chromosomes 3, 9 and 12. How many independent signals can we claim from this plot alone?

- A. Eight, one for each variant.
  - Feedback: Nearby variants are often in LD. Several of them can point to the same single signal.
- B. Three causal variants, one for each region.
  - Feedback: A region with a signal is not proof of one causal variant. The cause may be a variant we did not test.
- C. At most three regions, until we check LD between the variants. (correct)
  - Feedback: Yes. The plot shows where the signals are. Clumping at step 7.5 tells us how they group.

### 7.4 Multiple-testing thresholds

This scan has 236,815 tests, so its Bonferroni threshold is about 2.11e-7. A variant has p = 1e-7. How do we classify it?

- A. Significant under both thresholds.
  - Feedback: 1e-7 is larger than 5e-8, so it does not pass the usual GWAS threshold.
- B. It passes the Bonferroni threshold for this scan, but not the usual 5e-8 threshold. (correct)
  - Feedback: Yes. The usual threshold is stricter. It allows for about one million independent common variants in the genome, not only the tests in this scan.
- C. Not significant under either threshold.
  - Feedback: 1e-7 is smaller than 2.11e-7, so it passes the Bonferroni threshold for this scan.

### 7.5 Clump correlated results

We change the LD threshold for clumping and the number of clumps changes. What has changed?

- A. Only how we group the variants into signals. (correct)
  - Feedback: Yes. Clumps depend on the LD threshold, the distance and the samples used to measure LD.
- B. The p-values of the variants.
  - Feedback: Clumping only reads the results. The association scan and its p-values stay the same.
- C. The number of causal variants in the data.
  - Feedback: The data are the same. Only our summary of them has changed.

### 7.6 Regional plot

In each regional plot, the lead variant is the black diamond at the top. What does it tell us?

- A. It is the causal variant of the region.
  - Feedback: It has the smallest p-value among the sites we tested. The cause may be a variant we did not measure.
- B. The gene nearest to it is the cause.
  - Feedback: Distance is a weak guide. A signal can act on a gene further away.
- C. It marks the strongest association among the tested sites, and it may tag a cause in LD with it. (correct)
  - Feedback: Yes. Fine-mapping and other data are needed to go further.

### 7.7 Compare without PCs and without QC

Without PCs, lambda rises from about 1.016 to about 1.546, and the hits rise from 8 to 15. What is the most likely reason?

- A. The PCs were hiding real signals.
  - Feedback: Extra hits that appear only when we remove the adjustment are a warning sign, not discoveries.
- B. Differences in ancestry between cases and controls inflate the tests across the genome. (correct)
  - Feedback: Yes. The PCs capture these differences. Without them, many tests move away from the null together.
- C. Many small true effects across the genome.
  - Feedback: Many small true effects can raise lambda a little in large studies. A jump this big, when only the PCs change, points to population structure.

### 7.8 Final summary and reporting

Which evidence would be most important before we call a simulated association a biological discovery?

- A. Replication in independent real data, with suitable biological evidence. (correct)
  - Feedback: Yes. A simulation can teach the method, but it cannot show biology.
- B. A smaller p-value in the same data.
  - Feedback: A smaller p-value in the same data does not protect against bias or chance in that data.
- C. A larger odds ratio.
  - Feedback: A larger effect is not more likely to be true. The first estimates of an effect are often too large.

## Notes for review

- 7.2, option C: "the ratio of the median test statistic to the value we expect under no association" is the usual definition of lambda. Check that it matches the text of step 7.2.
- 7.4: the reason for 5e-8 ("about one million independent common variants") is the classic one for European ancestry. Check that the course gives the same reason.
- 7.7, option C, brings in inflation from many small true effects. The course may not cover it. A simpler wrong option would be: "The QC removed too many samples." (The QC is the same in both analyses.)
- 7.8, option C, brings in the idea that first estimates are too large (winner's curse). The course may not cover it either.
- The older draft `docs/review/self_assessment_draft.md` (commit d9e8f19) has two numbers for module 7 that no longer match the 2026.4 step JSON: 236,820 tests (now 236,815) and lambda without PCs about 1.527 (now about 1.546). Its questions check facts. The questions here check reasoning. The two drafts can live together, or this one can replace module 7 of the older draft.
