"""Hook file for PyInstaller."""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all data files and submodules for spaCy
datas = collect_data_files('spacy')
hiddenimports = collect_submodules('spacy')

# Collect data files for the specific model
datas += collect_data_files('fr_core_news_sm')
hiddenimports += collect_submodules('fr_core_news_sm')
