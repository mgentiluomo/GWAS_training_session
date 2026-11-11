#!/usr/bin/env python3
"""Build the portable student tutorial from tested notebooks and demo outputs.

Authoring dependency: matplotlib. Students need only a browser to read the result.
Run the demo validation first, then: python3 scripts/build_tutorial.py
"""
from pathlib import Path
import base64
import csv
import hashlib
import html
import io
import json
import re
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tutorial"
DL = OUT / "downloads"
DL.mkdir(parents=True, exist_ok=True)
REPO = "https://github.com/mgentiluomo/GWAS_training_session"
BRANCH = "course/2026-guided-training"
RAW = "https://raw.githubusercontent.com/mgentiluomo/GWAS_training_session/" + BRANCH
PROJECT = REPO + "/archive/refs/heads/" + BRANCH + ".zip"
QCDIR = ROOT / "results/demo/01_qc"
DEMO = ROOT / "data/demo"


def read_tsv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def esc(text):
    return html.escape(str(text), quote=True)


notebook = (ROOT / "lessons/01_quality_control.Rmd").read_text()
chunks = dict(re.findall(r"^```\{r\s+([^,}\s]+)[^\n]*\}\n(.*?)^```\s*$", notebook, re.M | re.S))


def block(text, label="R · run in RStudio"):
    return ('<div class="codebox"><span class="code-label">' + esc(label) +
            '</span><button class="copy-button" type="button" aria-label="Copy this code block">Copy</button>' +
            '<pre><code>' + esc(text.strip()) + '</code></pre></div>')


def code(label):
    return block(chunks[label])


def table(headers, rows, caption=None):
    return '<div class="table-wrap"><table>' + (f'<caption>{esc(caption)}</caption>' if caption else '') + \
        '<thead><tr>' + ''.join(f'<th scope="col">{esc(h)}</th>' for h in headers) + '</tr></thead><tbody>' + \
        ''.join('<tr>' + ''.join(f'<td>{esc(cell)}</td>' for cell in row) + '</tr>' for row in rows) + \
        '</tbody></table></div>'


def details(summary, body):
    return f'<details><summary>{esc(summary)}</summary><div class="detail-body">{body}</div></details>'


def callout(body, kind="note"):
    return f'<div class="{kind}">{body}</div>'


def checkpoint(label, checked_id):
    return f'<ul class="checklist"><li><label><input type="checkbox" data-progress="{checked_id}"><span>{label}</span></label></li></ul>'


def step(number, anchor, title, body):
    return f'<section class="step" id="{anchor}"><span class="step-no">Step {number}</span><h2>{title}</h2>{body}</section>'


def figure(data, bins, xlabel, title, threshold=None):
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.edgecolor": "#bccdca", "axes.labelcolor": "#173b4b"})
    fig, ax = plt.subplots(figsize=(8, 3.4), layout="constrained")
    ax.hist(data, bins=bins, color="#34796e", edgecolor="white", linewidth=.6)
    ax.set(xlabel=xlabel, ylabel="Count", title=title)
    ax.grid(axis="y", alpha=.15)
    if threshold is not None:
        ax.axvline(threshold, color="#a35422", linestyle="--", label=f"Course threshold: {threshold:g}")
        ax.legend(frameon=False)
    bio = io.BytesIO()
    fig.savefig(bio, format="png", dpi=150, facecolor="white")
    plt.close(fig)
    return base64.b64encode(bio.getvalue()).decode()


sample_missing = [float(r['F_MISS']) for r in read_tsv(QCDIR / 'before.smiss')]
variant_missing = [float(r['F_MISS']) for r in read_tsv(QCDIR / 'before.vmiss')]
het_f = [float(r['F']) for r in read_tsv(QCDIR / 'heterozygosity.het')]
counts = read_tsv(QCDIR / 'sample_variant_counts.tsv')
assert len(sample_missing) == 600 and len(variant_missing) == 6000
assert counts[-1]['samples'] == '592' and counts[-1]['variants'] == '5920'


def img(data, alt, caption):
    return f'<figure class="figure"><img src="data:image/png;base64,{data}" alt="{esc(alt)}" loading="lazy"><figcaption>{caption}</figcaption></figure>'


# Only explicitly enumerated synthetic inputs/checkpoints enter public downloads.
PACKAGES = []


def make_package(name, title, files, count_rows=None):
    path = DL / name
    members = {}
    for src in files:
        src = Path(src)
        relative = src.relative_to(ROOT)
        if not (str(relative).startswith('data/demo/') or str(relative).startswith('results/demo/')):
            raise ValueError('Refusing to package a non-demo input')
        if src.suffix == '.fam':
            for line in src.read_text().splitlines():
                assert line.split()[0].startswith('DEMO_') and line.split()[1].startswith('DEMO_')
        members[str(relative)] = src.read_bytes()
    if count_rows:
        s = io.StringIO()
        writer = csv.DictWriter(s, fieldnames=['stage', 'samples', 'variants'], delimiter='\t', lineterminator='\n')
        writer.writeheader(); writer.writerows(count_rows)
        members['results/demo/01_qc/sample_variant_counts.tsv'] = s.getvalue().encode()
    manifest = {'description': title, 'data': 'SIMULATED ONLY', 'seed': 20261111,
                'plink': '2.0 beta 1.4 (7 November 2026)',
                'files': {p: hashlib.sha256(b).hexdigest() for p, b in members.items()}}
    members['CHECKPOINT_MANIFEST.json'] = json.dumps(manifest, indent=2).encode()
    members['CHECKPOINT_README.txt'] = (
        title + '\nSIMULATED PRACTICE DATA ONLY. No real participant records.\n'
        'Extract into the RStudio project root, preserving data/ and results/ paths.\n'
        'Use mode="demo". Back up an existing run before replacing checkpoint files.\n'
        'These files belong to the documented demo seed/build and default course settings.\n'
        'They are not expected results for the original class dataset.\n').encode()
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for member, data in members.items():
            info = zipfile.ZipInfo(member, date_time=(2026, 11, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    PACKAGES.append({'file': name, 'title': title, 'bytes': path.stat().st_size,
                     'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'members': sorted(members)})


make_package('demo_input.zip', 'Initial demo input — 600 samples, 6000 variants',
             [DEMO / n for n in ('DB_demo.bed', 'DB_demo.bim', 'DB_demo.fam', 'README.txt',
                                 'Sex.txt', 'general_covar.txt', 'pheno.txt')])
meta_files = [ROOT / 'results/demo' / n for n in ('metadata.tsv', 'phenotype.tsv', 'sex.tsv')]
stages = [('01_autosomes', 'qc_01_autosomes.zip', 'After autosomal preparation', 1),
          ('02_geno', 'qc_02_geno.zip', 'After variant-missingness filtering', 2),
          ('03_mind', 'qc_03_mind.zip', 'After sample-missingness filtering', 3),
          ('04_maf', 'qc_04_maf.zip', 'After minor-allele-frequency filtering', 4),
          ('qc_final', 'qc_final.zip', 'Final QC checkpoint — ready for lesson 2', 5)]
for prefix, filename, title, nstages in stages:
    make_package(filename, title, [QCDIR / (prefix + ext) for ext in ('.bed', '.bim', '.fam')] + meta_files,
                 count_rows=counts[:nstages])
(DL / 'manifest.json').write_text(json.dumps({'data': 'SIMULATED ONLY', 'packages': PACKAGES}, indent=2))


def download(name, text="Download checkpoint"):
    return f'<a class="button secondary" href="{RAW}/tutorial/downloads/{name}" download>{esc(text)}</a>'


def end(previous, next_):
    return f'<div class="page-end"><a href="#{previous[0]}">← {previous[1]}</a><a href="#{next_[0]}">{next_[1]} →</a></div>'


home = f'''
<span class="eyebrow">Genetic and genomic data analysis · University of Pisa</span>
<h1>From genotype data<br>to association analysis.</h1>
<p class="lead">A practical GWAS tutorial you can follow in class and return to at your own pace. Understand the question, run a small step, check the result.</p>
<p class="quiet">Manuel Gentiluomo · University of Pisa</p>
<div class="actions"><a class="button" href="#setup">Prepare your computer</a><a class="button secondary" href="#qc">Start the QC walkthrough</a></div>
<div class="cards">
<article class="card"><span class="step-no">Module 01 · Core pathway</span><h3>Quality control</h3><p>Meet the files, investigate missing calls and document which samples and variants remain.</p><span class="pill">Guided web lesson</span><a class="card-link" href="#qc">Open the walkthrough →</a></article>
<article class="card"><span class="step-no">Module 02 · Core pathway</span><h3>Population structure</h3><p>Explore genetic similarity with PCA and prepare a defensible analysis sample set.</p><span class="pill">RStudio notebook</span><a class="card-link" href="{REPO}/blob/{BRANCH}/lessons/02_population_structure.Rmd">Open lesson 2 on GitHub →</a></article>
<article class="card"><span class="step-no">Module 03 · Core pathway</span><h3>Association</h3><p>Compare logistic models and interpret odds ratios, Manhattan plots and QQ plots.</p><span class="pill">RStudio notebook</span><a class="card-link" href="{REPO}/blob/{BRANCH}/lessons/03_association.Rmd">Open lesson 3 on GitHub →</a></article>
</div>
<div class="hero"><h2>One task at a time. More than one way to keep up.</h2><p>Run the core steps first. If you are ready for more, try a challenge. If your computer is blocked, read the worked outputs or use a matching checkpoint and return to the error later.</p><a href="#help">Find a way back into the lesson →</a></div>
<div class="two-col"><section><h2>What you need</h2><ul><li>Basic experience opening a table in R.</li><li>Your own Windows, macOS or Linux computer.</li><li>R, RStudio and PLINK 2 for the analytical work.</li></ul><p>You can read the tutorial and try its browser exercises without installing the analysis software.</p></section><section><h2>What you will produce</h2><ul><li>An auditable QC count table.</li><li>PCA and an explicit sample list.</li><li>Association results and a short interpretation.</li></ul><p>The modules can be used separately or combined. One suggested teaching route uses three four-hour sessions, including breaks.</p></section></div>
{callout('<strong>Practice data, clearly labelled.</strong> This web walkthrough uses a simulated dataset: 600 samples and 6,000 variants. The original class data use a separate access route. Demo results cannot support a claim about a real disease.', 'warning')}
<h2>Use the modules across courses</h2><p>These are independent teaching materials by Manuel Gentiluomo for students at the University of Pisa. Use a single topic, follow the complete GWAS pathway, or return to an example for self-study.</p><p>One possible teaching context is <em>Omics: Biotechnology and AI for Health</em> (552EE), in the MSc in Biotechnologies and Applied Artificial Intelligence for Health. The resource has a broader scope and can support other genetics, genomics, biotechnology and bioinformatics teaching.</p><p>Choose the preparation and file-format sections if you are new to the tools. If you already know them, move to the analytical modules and optional challenges. Teaching time and module selection can be adapted to each course.</p><h2>How to use a lesson</h2>{table(['Understand','Run','Check','Interpret'],[['Read the question and the figure.','Run one R chunk in the supplied notebook.','Compare the file, shape and count.','Explain what changed and why it matters.']])}
{end(('home','Tutorial home'),('setup','Prepare your computer'))}
'''

setup = f'''
<span class="eyebrow">Before the class</span><h1>A working starting point.</h1>
<p class="lead">Keep your computer in your preferred language. We use explicit file conventions and a single RStudio project.</p>
<h2>1. Download the complete project</h2><p>Download the ZIP and extract it into a writable local folder. Open <code>GWAS_training_session.Rproj</code>. Keep its folders together; do not move individual notebooks into a new folder.</p>
<div class="actions"><a class="button" href="{PROJECT}">Download the RStudio project</a><a class="button secondary" href="{REPO}/tree/{BRANCH}">Browse the source on GitHub</a></div>
<p class="quiet">This preview points to the review branch. The main branch is not yet the revised course.</p>
<h2>2. Install R and RStudio</h2><p>Install <a href="https://cran.r-project.org/">R</a> first, then <a href="https://posit.co/download/rstudio-desktop/">RStudio Desktop</a>. Open the project and find the R console: it usually has a <code>&gt;</code> prompt.</p>
{block('getwd()\nfile.exists("config.R")','R console · check the project')}
{callout('<strong>Check:</strong> the second command returns <code>TRUE</code>. If not, reopen the project instead of editing paths in every lesson.', 'check')}
<h2>3. Add PLINK 2 for your system</h2><p>Download from the <a href="https://www.cog-genomics.org/plink/2.0/">official PLINK 2 page</a>, extract the archive, and put the executable in the project’s <code>bin/</code> folder. The tested Linux build is beta 1.4, 7 November 2026; record the actual build you use.</p>
<div class="os-buttons" role="group" aria-label="Operating system instructions"><button type="button" data-os="windows" aria-pressed="true">Windows</button><button type="button" data-os="mac" aria-pressed="false">macOS</button><button type="button" data-os="linux" aria-pressed="false">Linux</button></div>
<section class="os-panel" data-os-panel="windows"><h3>Windows</h3><p>Select the appropriate 64-bit build. Put <code>plink2.exe</code> directly in <code>bin/</code>. Windows may hide known filename extensions: check the file type and avoid accidentally naming it <code>plink2.exe.exe</code>.</p></section>
<section class="os-panel" data-os-panel="mac"><h3>macOS</h3><p>Select ARM64 for Apple Silicon or the matching Intel build for an Intel Mac. Put <code>plink2</code> in <code>bin/</code>. If necessary, run <code>Sys.chmod("bin/plink2", "0755")</code> in the R console. Follow the standard macOS approval process for a trusted official download.</p></section>
<section class="os-panel" data-os-panel="linux"><h3>Linux</h3><p>Select a build compatible with the CPU. Put <code>plink2</code> in <code>bin/</code>. If necessary, run <code>Sys.chmod("bin/plink2", "0755")</code> in the R console. A working executable on PATH is also supported.</p></section>
{callout('The analytical workflow has been executed on Linux. The Windows and macOS instructions still require checks on those systems. Do not disable system security to run a download.', 'warning')}
<h2>4. Create or download the demo inputs</h2><p>Leave <code>mode = "demo"</code> in <code>config.R</code>. Create the data in the R console:</p>
{block('source("scripts/create_demo.R")')}
<p>The final table should report <strong>600 samples and 6000 variants</strong>. If you cannot generate it yet, download the same input files and extract them into the project root, preserving the <code>data/demo/</code> path.</p>
{download('demo_input.zip','Download the demo input')}
<h2>5. Run the pre-class check</h2>{block('source("scripts/preflight.R")')}
<p>The check tests the executable, input-file consistency and PLINK read/write access in a path with spaces and non-English characters. It saves <code>results/demo/preflight.txt</code>. If it stops, keep the first error and visit <a href="#help">Troubleshooting</a>.</p>
<h2>Different languages, identical file conventions</h2>
{table(['Convention','Use','Avoid'],[['Decimal mark','23.5','23,5 in a course numeric field'],['Column separator','Tabs in metadata TSV','Assuming every .csv uses the same delimiter'],['Thousands grouping','12500','12,500 or 12.500'],['Sample identifiers','Text, e.g. 00123','Dropping initial zeros'],['Text encoding','UTF-8','An undocumented export encoding']])}
<p>The setup sets decimal display to a point in the current R session. It does not change your operating-system language. The importer rejects ambiguous numeric fields rather than guessing.</p>
{details('Why a comma is not always a decimal mark','<p>In one file, <code>1,234</code> may mean one point two three four; in another, one thousand two hundred thirty-four. A blanket replacement can corrupt data. Confirm the documented delimiter and decimal convention before converting an external file.</p>')}
<p><a href="{REPO}/blob/{BRANCH}/docs/international_setup.md">Read the detailed international-settings guide →</a></p>
<h2>Your ready checklist</h2>
{checkpoint('The complete RStudio project opens, and config.R exists.','ready-project')}
{checkpoint('PLINK 2 reports a working version.','ready-plink')}
{checkpoint('The demo BED/BIM/FAM set is present and preflight passes.','ready-data')}
{checkpoint('I can distinguish the R console, terminal and notebook editor.','ready-panes')}
{end(('home','Tutorial home'),('qc','Open quality control'))}
'''

recovery = '''root <- if (file.exists("R/course.R")) "." else ".."
source(file.path(root, "R", "course.R"))
cfg <- course_config(root)
start <- file.path(cfg$qc, "01_autosomes")
geno <- file.path(cfg$qc, "02_geno")
mind <- file.path(cfg$qc, "03_mind")
maf <- file.path(cfg$qc, "04_maf")
prune <- file.path(cfg$qc, "prune")
king <- file.path(cfg$qc, "relatedness")
final <- file.path(cfg$qc, "qc_final")'''

fam_head = [line.split() for line in (DEMO/'DB_demo.fam').read_text().splitlines()[:3]]
bim_head = [line.split() for line in (DEMO/'DB_demo.bim').read_text().splitlines()[:3]]
qc = '''<span class="eyebrow">Module 01 · Core walkthrough</span><h1>Quality control.<br>Keep track of every decision.</h1>
<p class="lead">Before testing association, ask whether the genotype data are sufficiently complete and whether the samples fit the planned analysis.</p>
<p>Open <code>lessons/01_quality_control.Rmd</code> in RStudio. Read this page alongside it. Run one chunk at a time; the web page itself does not run R or PLINK.</p>
<nav class="section-toc" aria-label="Quality control steps"><a href="#qc-start">1. Start a clean session</a><a href="#qc-files">2. Understand the files</a><a href="#qc-baseline">3. Establish the baseline</a><a href="#qc-missing">4. Inspect missingness</a><a href="#qc-filter">5. Filter and count</a><a href="#qc-het">6. Review heterozygosity</a><a href="#qc-related">7. Review relatedness</a><a href="#qc-finish">8. Save the checkpoint</a></nav>'''
qc += step('01','qc-start','Start a clean session.',
    '<p>Open the project and restart R. Use the notebook’s Run button if keyboard shortcuts differ on your keyboard. The first chunk loads the shared helpers and checks the matching genotype files.</p>' + code('qc-setup') +
    callout('<strong>Check:</strong> the data mode says <code>demo (SIMULATED data)</code> and the input counts are 600 samples and 6000 variants. A missing-file error means setup is incomplete; do not run later chunks yet.','check') +
    table(['Location','What belongs there','Example'],[['R console','R expressions','2 + 2'],['Terminal','Operating-system commands','plink2 --version'],['Notebook editor','Saved instructions and executable R chunks','run_plink(...)']]) +
    '<p><code>run_plink()</code> is R code that starts an external program. The printed PLINK command is a record of the operation, not another R expression to paste into the console.</p>')
qc += step('02','qc-files','Three files describe one genotype dataset.',
    '<p>The binary calls, variant information and sample information belong together. Their order matters: a matching filename alone does not prove that the three files come from the same release.</p>' +
    '<div class="file-family"><article class="file-tile"><strong>.bed</strong><p>Packed genotype calls. Do not open or edit it as a text table.</p></article><article class="file-tile"><strong>.bim</strong><p>One row per variant: location, identifier and two alleles.</p></article><article class="file-tile"><strong>.fam</strong><p>One row per sample: identifiers, parents, sex and phenotype.</p></article></div>' +
    table(['FID','IID','Father','Mother','Sex','Phenotype'],fam_head,'Example: first three rows of the simulated FAM') +
    table(['Chromosome','Variant ID','cM','Position','A1','A2'],bim_head,'Example: first three rows of the simulated BIM') +
    '<p>For the course’s binary outcome, <code>1 = control</code> and <code>2 = case</code>. In the original class input, a FAM phenotype may be unavailable until updated from the external phenotype file. We use explicit external metadata in both modes.</p>' +
    code('qc-inspect-files') +
    callout('<strong>Check:</strong> the metadata match genotyped people by both FID and IID. Identifier zeros stay intact. Missing or duplicate ID pairs stop the import.','check') +
    details('Pause and explain: where would you find a variant’s physical position?', '<p>Inspect column 4 of the BIM file. To connect a covariate record to the right sample, match the FID/IID pair, not the row number.</p>'))
qc += step('03','qc-baseline','Establish a baseline before filtering.',
    '<p>We retain autosomes for this core exercise, update recorded sex and load the binary phenotype. Original input files are not overwritten.</p>' + code('qc-prepare') +
    table(['Argument','What it does'],[['--bfile','Names the input BED/BIM/FAM prefix'],['--autosome','Selects chromosomes 1–22'],['--update-sex','Reads the explicit sex-code file'],['--pheno / --pheno-name','Loads the named Disease outcome'],['--make-bed','Writes a new matching genotype set'],['--out','Names the output prefix and log files']]) +
    callout('<strong>Check:</strong> find <code>01_autosomes.bed/.bim/.fam</code>, <code>before.smiss</code> and <code>before.vmiss</code> under <code>results/demo/01_qc/</code>. The baseline still has 600 samples and 6000 variants.','check') +
    download('qc_01_autosomes.zip') +
    '<p class="quiet">Sex-chromosome analysis needs genome-build and PAR checks. It is an extension, rather than an implicit part of the autosomal walkthrough.</p>')
qc += step('04','qc-missing','Look at missingness before choosing a cutoff.',
    '<p>A missing genotype is an uncalled sample–variant entry. Sample missingness uses variants as the denominator; variant missingness uses samples. A 5% missingness threshold corresponds to a 95% call rate.</p>' +
    img(figure(sample_missing,30,'Missing genotype fraction per sample','Sample missingness before filtering',.10),
        'Histogram of 600 simulated samples, with a dashed line at 10% missing calls.',
        'Actual demo diagnostic before QC filtering. Six samples have deliberately elevated missingness.') +
    img(figure(variant_missing,30,'Missing genotype fraction per variant','Variant missingness before filtering',.05),
        'Histogram of 6000 simulated variants, with a dashed line at 5% missing calls.',
        'The denominator here is the number of samples, rather than the number of variants.') +
    '<div class="interactive"><span class="eyebrow">Explore the diagnostic</span><h3>Move the sample-missingness threshold.</h3><label for="missingness-threshold">Maximum missing fraction: <output id="threshold-label">10%</output></label><input id="missingness-threshold" type="range" min="0" max="25" value="10" step="1"><div class="metric-row" aria-live="polite"><div class="metric"><strong id="retained-count">594</strong><span>samples meeting this criterion</span></div><div class="metric"><strong id="excluded-count">6</strong><span>samples above the threshold</span></div></div><p class="quiet">Calculated from the 600 actual demo baseline missingness values. This browser exercise changes no files. Full-pipeline counts can differ after earlier filtering changes the denominator.</p></div>' +
    code('qc-missingness') +
    '<div class="quiz" data-quiz data-correct="a" data-explanation="A sample at 9% passes a 10% sample-missingness threshold; a variant at 6% fails a 5% variant-missingness threshold. Each threshold has its own denominator."><fieldset><legend>A sample has 9% missing calls; a variant has 6%. With mind = 0.10 and geno = 0.05, what passes?</legend><label><input type="radio" name="missingness-quiz" value="a">The sample passes; the variant fails.</label><label><input type="radio" name="missingness-quiz" value="b">The sample fails; the variant passes.</label><label><input type="radio" name="missingness-quiz" value="c">Both pass.</label></fieldset><button class="button secondary" type="button">Check my reasoning</button><div class="feedback" role="status"></div></div>')
filter_lines = chunks['qc-filters'].strip().splitlines()
geno_code = '\n'.join(filter_lines[:3]); mind_code = '\n'.join(filter_lines[3:6]); maf_code = '\n'.join(filter_lines[6:])
qc += step('05','qc-filter','Apply one filter, then count.',
    '<p>The course uses teaching thresholds: variant missingness 5%, sample missingness 10%, and MAF 1%. These are choices to examine, not values to transfer automatically to any study.</p>' +
    '<h3>A. Variant missingness: --geno 0.05</h3><p>Remove variants with missing calls in more than 5% of samples.</p>' + block(geno_code) +
    callout('Demo checkpoint: <strong>600 samples · 5970 variants</strong>. Thirty deliberately poorly called variants are removed.','check') + download('qc_02_geno.zip') +
    '<h3>B. Sample missingness: --mind 0.10</h3><p>Now remove samples whose missing fraction exceeds 10% on the remaining variants.</p>' + block(mind_code) +
    callout('Demo checkpoint: <strong>594 samples · 5970 variants</strong>. Six samples are removed.','check') + download('qc_03_mind.zip') +
    '<h3>C. Minor allele frequency: --maf 0.01</h3><p>Remove variants with minor allele frequency below 1% in the current sample set. MAF is an allele frequency, not the proportion of people carrying the allele.</p>' + block(maf_code) +
    callout('Demo checkpoint: <strong>594 samples · 5920 variants</strong>. Fifty low-frequency variants are removed.','check') + download('qc_04_maf.zip') +
    details('Why can the order matter?','<p>Each filter is calculated using the samples and variants present at that step. Removing poorly called variants can reduce a sample’s measured missingness; removing samples can change allele frequencies. Keep the order and its count table with your results.</p>') +
    checkpoint('I can explain which denominator is used by geno, mind and MAF.','qc-filters'))
qc += step('06','qc-het','Review unusual heterozygosity.',
    '<p>Estimate the inbreeding coefficient on common, approximately independent variants. LD pruning limits the influence of highly correlated markers. The pruned set is for diagnostics, not automatically the final association dataset.</p>' + code('qc-pruning-and-het') +
    img(figure(het_f,30,'Estimated F coefficient','Heterozygosity review'),
        'Histogram of F coefficients in the simulated post-missingness and MAF dataset.',
        'F compares observed and expected heterozygosity. Review the pattern together with structure and technical information.') +
    code('qc-het-plot') +
    callout('An unusual coefficient can reflect technical problems, ancestry or inbreeding. A pooled mean ±3 SD rule can remove valid samples from a heterogeneous cohort. This walkthrough reports the diagnostic without automatic heterozygosity exclusions.','warning') +
    details('Going further: what else would you ask before excluding a sample?','<p>Review call quality, batch, contamination evidence, population structure and whether the coefficient was estimated using appropriate allele frequencies. Record the rationale and repeat downstream analysis after any justified exclusion.</p>'))
qc += step('07','qc-related','Avoid treating close relatives as independent.',
    '<p>The simple association models later in the course assume independent observations. KING estimates genetic kinship and selects a subset avoiding pairs above the chosen threshold.</p>' +
    table(['Relationship','Approximate KING kinship'],[['Duplicate / identical genotype','0.50'],['First degree','0.25'],['Second degree','0.125'],['Third degree','0.0625']]) +
    '<p>The teaching cutoff is <code>0.0884</code>, screening close relationships through roughly the second degree. Estimates are variable; KING kinship is not the same quantity as PI_HAT.</p>' + code('qc-relatedness') +
    callout('<strong>Check:</strong> the demo finishes with 592 samples and 5920 variants. Two simulated duplicate pairs lead to two exclusions. Apply the retained <em>sample</em> list to all QC-passing variants, rather than keeping only the LD-pruned markers.','check') +
    details('How would sample selection change in a research study?','<p>Call quality, phenotype completeness and the study design can affect which relative should be retained. A mixed-model strategy may instead accommodate related observations. The automatic teaching subset is not a universal sample-priority rule.</p>'))
qc += step('08','qc-finish','Save a checkpoint you can explain.',
    table(['Stage','Samples','Variants'],[[r['stage'],r['samples'],r['variants']] for r in counts],
          'Verified output for the default simulated walkthrough') +
    '<p>Your checkpoint is <code>qc_final.bed/.bim/.fam</code>, alongside the prepared metadata, phenotype file and count table. Lesson 2 reloads these files; it does not require a saved R workspace.</p>' + download('qc_final.zip','Download the lesson 2 starting checkpoint') +
    '<h3>Before moving on</h3><p>Explain why the sample count decreases at the relatedness step while the variant count remains the same. Then name the file you would inspect if the counts did not match your prediction.</p>' +
    details('Compare your explanation','<p>The KING cutoff supplies a retained-sample list. It is applied to the full MAF-filtered set, so relatives can be removed without intentionally discarding its variants. Inspect the PLINK log and sample/variant count table; counts alone do not validate every QC decision.</p>') +
    checkpoint('I have a complete final genotype set and can account for the exclusions.','qc-checkpoint') +
    '<div class="hero"><h2>Ready for population structure.</h2><p>Next, use the QC-passing data to calculate PCs, inspect structure and prepare an explicit analysis sample list.</p>' +
    f'<a class="button" href="{REPO}/blob/{BRANCH}/lessons/02_population_structure.Rmd">Open the PCA notebook</a></div>')
qc += end(('setup','Preparation'),('practice','Practice and explain'))

practice = '''<span class="eyebrow">Module 01 · Practice</span><h1>Make the decisions yours.</h1>
<p class="lead">Predict first. Run a separate comparison if you can. Use the explanation only after you have tried.</p>
<h2>1. Call rate is not missingness</h2><p>A new sample has a call rate of 94%. A protocol keeps samples with missingness at most 0.08. Does it pass this criterion? Show the conversion.</p>'''
practice += details('Reveal a worked explanation','<p>Its missing fraction is <code>1 − 0.94 = 0.06</code>, or 6%. It passes the 8% missingness criterion. This says nothing about whether it passes other QC criteria.</p>')
practice += '''<h2>2. A stricter cutoff</h2><p>Before running a new command, predict what reducing <code>mind</code> from 0.10 to 0.05 can do to the retained sample set for the same input. Use a new output prefix such as <code>03_mind_stricter</code>; do not overwrite the core result.</p>'''
practice += details('A hint, without running it','<p>The same input and denominator are essential. Ask whether a sample failing the original rule could pass a more restrictive version of that rule.</p>')
practice += details('Reveal the reasoning','<p>The number retained cannot increase for the same fixed input, though it may stay equal. The exact difference depends on the data. Repeating the whole pipeline can change other estimates, so separate the one-step comparison from a complete rerun.</p>')
practice += '''<h2>3. The mixed file set</h2><p>A BED file downloaded yesterday is combined with a BIM from another release. The names match and both files open. What would you check before running QC?</p>'''
practice += details('Reveal the reasoning','<p>Check provenance and release, sample/variant order, dimensions and the BED signature/expected byte count. Equal dimensions alone cannot prove that the biological records are matched. Obtain a known matching set rather than relabelling files to bypass a check.</p>')
practice += '''<h2>4. A problematic import</h2><p>An exported file has header <code>FID;IID;Age</code> and a value <code>24,5</code>. Explain why renaming it to <code>.tsv</code> is insufficient. What information is needed before conversion?</p>'''
practice += details('Reveal the reasoning','<p>Renaming does not change delimiters, decimal marks or encoding. Confirm the documented semicolon separator, decimal comma, missing-value coding, text encoding and identifier handling, then import with those settings and validate a new canonical output. Do not replace all commas blindly.</p>')
practice += '''<h2>Write your QC note</h2><p>In five sentences, name the data mode and starting dimensions, explain two filtering choices, give the final dimensions, identify a diagnostic needing review and state one limitation of this walkthrough. Keep your note in your own lab notebook.</p>'''
practice += checkpoint('I have written a QC interpretation, including a limitation.','qc-interpretation')
practice += callout('This page does not submit answers or collect student records. Checklist ticks can remain in this browser; exercise responses are not saved or sent.')
practice += end(('qc','Quality control'),('downloads','Files and checkpoints'))

package_html = []
for p in PACKAGES:
    kb = p['bytes'] / 1024
    package_html.append(f'<article class="package"><div><h3>{esc(p["title"])}</h3><p>{esc(p["file"])} · {kb:.0f} KB · simulated only</p></div>{download(p["file"],"Download ZIP")}</article>')

downloads = f'''<span class="eyebrow">Files and checkpoints</span><h1>The right files<br>for the right step.</h1>
<p class="lead">Every package below contains simulated data only. Extract it into the project root and preserve its internal folders.</p>
{callout('These packages match the default demo seed and tested build. They are not checkpoints for the original class dataset, or for a run whose sample selection or thresholds you changed. Back up an existing run before replacing outputs.','warning')}
<div class="actions"><a class="button" href="{PROJECT}">Complete RStudio project</a><a class="button secondary" href="{REPO}/tree/{BRANCH}/lessons">All three notebooks</a></div>
<div class="package-list">{''.join(package_html)}</div>
<h2>Resume without restoring an old workspace</h2><ol><li>Keep the first error and the log from the run that stopped.</li><li>Back up the affected outputs. Restore the package for the last completed step into the project root.</li><li>Open the RStudio project and restart R. Run the setup below.</li><li>Use the individual command block for the next step on this web page, or select those lines in the notebook. An intermediate package does not contain every earlier diagnostic or genotype set.</li></ol>
{block(recovery,'R · restore path variables only')}
<p>For a full restart, restore the initial demo inputs and begin the QC walkthrough at step 1. To join lesson 2 directly, use the final QC checkpoint and open its notebook.</p>
<h2>What is inside a checkpoint?</h2><p>The matching BED/BIM/FAM set for that stage, prepared metadata, phenotype and sex tables, a stage-appropriate count table and a manifest with SHA-256 checksums. It does not include a saved R workspace or the original study data.</p>
<p><a href="{RAW}/tutorial/downloads/manifest.json">Inspect the package manifests and checksums</a></p>
<h2>The original class data</h2><p>The original BED is distributed through the course’s institutional access arrangements. Older links may expire or require authentication. Use only its matching BIM/FAM files and authorized checkpoints.</p>
<a href="{REPO}/blob/{BRANCH}/docs/data.md">Read original-data access and coding instructions →</a>
{end(('practice','Practice'),('help','Troubleshooting'))}'''

help_page = '''<span class="eyebrow">Troubleshooting</span><h1>Keep the first error.<br>Find a way back in.</h1>
<p class="lead">A technical problem does not need to end your participation. You can read the examples, interpret outputs and rejoin from a matching checkpoint.</p>
<div class="hero"><h2>When a chunk stops</h2><ol><li>Do not run later chunks yet.</li><li>Read the first error, not just the last line.</li><li>Inspect the input or log named in that message.</li><li>Use the relevant check below, or a checkpoint if the class is moving on.</li></ol></div>'''
issues = [
    ('R cannot open R/course.R', '<p>Open the complete RStudio project. In the console, <code>file.exists("config.R")</code> should be TRUE. Do not move the notebook into a separate folder or translate folder names by hand.</p>'),
    ('PLINK 2 was not found', '<p>Extract the executable from its ZIP and place it directly in <code>bin/</code>: plink2.exe on Windows, plink2 on macOS/Linux. A PLINK 1.9 executable is not sufficient. Confirm that the build matches your OS and CPU.</p>'),
    ('A downloaded program cannot execute', '<p>Check CPU architecture, file permissions and the operating system’s normal approval process for a trusted official download. On macOS/Linux, <code>Sys.chmod("bin/plink2", "0755")</code> grants executable permission to that file. Do not disable security globally.</p>'),
    ('BED header or size does not match', '<p>Check whether a login webpage was saved instead of binary data. Confirm that BED, BIM and FAM are from the same release. Obtain the matching set; do not rename unrelated files to pass the check.</p>'),
    ('The table has one column, or a number is rejected', '<p>Check the actual delimiter, decimal mark and text encoding. Course metadata are UTF-8 TSV with decimal points. A semicolon CSV or decimal comma needs a documented separate import. Avoid an Excel open-and-resave round trip on analytical inputs.</p>'),
    ('Sample IDs are duplicated or do not match', '<p>Inspect the FID/IID pairs as text, including initial zeros. Resolve the data provenance. Do not join by row number or discard an identifier to force a match.</p>'),
    ('A file exists but a variable is not found', '<p>Files on disk and objects in R memory are different. Start with the notebook’s setup chunk. If restoring an intermediate package, run the path-variable setup on the Downloads page, then execute the next individual step.</p>'),
    ('My count differs from the example', '<p>Confirm demo mode, the original seed, filtering order and settings. Check the count table and the first differing PLINK log. The published numbers are for the default simulation, not the original study or an intentionally modified exercise.</p>'),
    ('A path with spaces or other alphabets fails', '<p>The course constructs and quotes paths, but platform verification is still needed. Preserve your original copy and try a short writable project location, such as C:/gwas_training on Windows or a gwas_training folder in your home directory. Rerun preflight and retain its report.</p>'),
    ('Knit fails but individual chunks work', '<p>The analytical code and HTML rendering have different dependencies. Run <code>source("scripts/install_packages.R")</code> and check knitr, rmarkdown and Pandoc. RStudio normally includes Pandoc. Continue reading this web tutorial while resolving the preview.</p>')]
help_page += ''.join(details(a,b) for a,b in issues)
help_page += '<h2>Rejoin the lesson</h2><p>Download a checkpoint for the same data mode, restore its complete file set and record which results were supplied. You can then interpret the next step with the class and return to the original error later.</p><div class="actions"><a class="button" href="#downloads">Choose a checkpoint</a><a class="button secondary" href="#qc">Read the worked walkthrough</a></div>'
help_page += end(('downloads','Files and checkpoints'),('glossary','Glossary'))

terms = [
    ('Genotype','The observed alleles for one sample at one position.'),('FID / IID','The identifier pair used to match samples across files.'),
    ('Call rate','The fraction of successfully called genotypes: one minus missingness.'),('MAF','Minor allele frequency in the samples used for the estimate.'),
    ('LD','Association between alleles at different loci; linked SNPs can carry correlated information.'),('LD pruning','Selecting an approximately independent subset for an analysis such as PCA.'),
    ('Heterozygosity','The presence of two different alleles at a diploid locus.'),('KING kinship','An estimate of genetic relationship; duplicates are near 0.5 on this scale.'),
    ('HWE','A population-genetic expectation for genotype proportions; departures need contextual interpretation.'),('PCA / PC','Principal component analysis and the components summarizing genetic variation.'),
    ('Covariate','An additional predictor, such as age or a PC, included in a statistical model.'),('OR','Odds ratio per extra copy of the counted allele in an additive logistic model.'),
    ('A1','The counted allele reported by the association output; do not assume it is always the minor allele.'),('Confidence interval','A range expressing uncertainty under the model’s assumptions.'),
    ('p-value','Under the null model, the probability of a statistic at least as extreme as observed.'),('Checkpoint','A matching set of saved files from a defined stage, not a guarantee of scientific validity.')]
glossary = '<span class="eyebrow">Quick reference</span><h1>A small glossary<br>for the practical work.</h1>' + table(['Term','Meaning'],terms)
glossary += f'<p><a href="{REPO}/blob/{BRANCH}/docs/glossary.md">Open the extended repository glossary →</a></p>'
glossary += '<h2>Reference documentation</h2><ul><li><a href="https://www.cog-genomics.org/plink/2.0/filter">PLINK filtering</a></li><li><a href="https://www.cog-genomics.org/plink/2.0/basic_stats">PLINK quality-control statistics</a></li><li><a href="https://www.cog-genomics.org/plink/2.0/distance">KING kinship</a></li><li><a href="https://stat.ethz.ch/R-manual/R-devel/library/utils/html/read.table.html">R file delimiters and decimal marks</a></li></ul>'
glossary += end(('help','Troubleshooting'),('home','Tutorial home'))

PAGES = [('home','Tutorial home',home),('setup','Before the class',setup),('qc','Quality control',qc),
         ('practice','Practice',practice),('downloads','Files and checkpoints',downloads),('help','Troubleshooting',help_page),('glossary','Glossary',glossary)]
nav = ''.join(f'<a class="nav-link" href="#{key}"><span class="nav-number">{str(i+1).zfill(2)}</span>{title}</a>' for i,(key,title,_) in enumerate(PAGES))
sections = ''.join(f'<article class="page" id="{key}" data-page="{key}" data-title="{esc(title)}">{body}</article>' for key,title,body in PAGES)
css = (ROOT/'tutorial_src/style.css').read_text()
js = (ROOT/'tutorial_src/app.js').read_text()
document = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GWAS Practical Tutorial · Manuel Gentiluomo</title><meta name="description" content="Independent GWAS teaching materials by Manuel Gentiluomo for students across University of Pisa courses. Quality control, RStudio setup and simulated-data checkpoints.">
<style>{css}</style></head><body>
<a class="skip" href="#main-content">Skip to content</a>
<aside class="rail" id="course-navigation"><a class="brand" href="#home">GWAS<br>Practical Tutorial<small>MANUEL GENTILUOMO</small></a><p class="rail-label">Your learning path</p><nav aria-label="Course navigation">{nav}</nav>
<div class="rail-foot"><strong>Open learning resources</strong><p>Genetic and genomic data analysis</p><div class="progress-wrap"><span id="progress-text"></span><div class="progress-track"><div class="progress-bar"></div></div><p id="progress-note"></p><button type="button" class="button secondary" id="reset-progress">Reset ticks</button></div></div></aside>
<div class="shell"><header class="topbar"><div><button type="button" class="menu-button" aria-controls="course-navigation" aria-expanded="false">Menu</button> <strong>GWAS Practical Tutorial</strong><span class="course-subtitle"> · University of Pisa</span></div><div class="header-links"><a href="{REPO}/tree/{BRANCH}">GitHub</a><a href="https://www.manuelgentiluomo.it/">Personal site</a><span class="badge">Review draft</span></div></header>
<main id="main-content" tabindex="-1"><noscript><p class="no-js">JavaScript is off. All written lessons remain below; the slider and interactive feedback need JavaScript. Download links require a connection.</p></noscript>{sections}</main>
<footer class="footer"><p>Manuel Gentiluomo · University of Pisa</p><p>Reading and browser exercises do not submit student responses. Checklist ticks are stored only in this browser when available. Demo data are simulated.</p><p>Draft web tutorial: preparation and lesson 1. Lessons 2–3 are available as RStudio notebooks. Linux analytical validation; Windows/macOS checks remain.</p></footer></div>
<div id="toast" class="toast" role="status" hidden></div>
<script type="application/json" id="sample-missingness-data">{json.dumps(sample_missing)}</script><script>{js}</script></body></html>'''
(OUT/'index.html').write_text(document)
print(f'Built {OUT.relative_to(ROOT)}/index.html ({len(document):,} characters), {len(PACKAGES)} demo downloads.')
