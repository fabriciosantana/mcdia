# MCDIA - Data Science and Machine Learning Educational Repository

MCDIA is an educational repository focused on Data Science and Machine Learning with Python. It contains Jupyter notebooks organized into courses and exercises, structured as both standalone notebooks and Git submodules.

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

## Repository Structure

- `00-python/` - Root directory with basic Python and pandas introductory notebooks
  - `basic/` - Contains `00-hello.ipynb` (Hello World introduction)
  - `pandas/` - Contains 6 pandas tutorial notebooks (01-05 series manipulation and dataframes)
- `mcdia-python/` - Git submodule containing advanced course content (Aulas/Aula1-Aula6)
- `mcdia-nivelamento/` - Git submodule containing leveling course content (day 01-04)
- `.vscode/` - VS Code settings configured for Python development with conda

## Working Effectively

### Bootstrap and Setup Repository
**ALWAYS run these exact commands in order. Set timeout to 60+ minutes for pip install. NEVER CANCEL.**

1. Clone repository with submodules:
   ```bash
   git clone --recursive https://github.com/fabriciosantana/mcdia.git
   ```

2. If submodules fail with SSH, configure HTTPS and retry:
   ```bash
   git config --file=.gitmodules submodule.mcdia-python.url https://github.com/fabriciosantana/mcdia-python.git
   git config --file=.gitmodules submodule.mcdia-nivelamento.url https://github.com/fabriciosantana/mcdia-nivelamento.git
   git submodule sync
   git submodule update --init --recursive
   ```

3. Install required Python packages:
   ```bash
   pip3 install pandas numpy jupyter
   ```
   - **CRITICAL**: This command takes 3-5 minutes to complete. NEVER CANCEL. Set timeout to 10+ minutes.

### Running the Environment

1. **Verify installation works:**
   ```bash
   python3 -c "
   import pandas as pd
   import numpy as np
   print('pandas version:', pd.__version__)
   print('numpy version:', np.__version__)
   print('Basic imports working!')
   "
   ```

2. **Start Jupyter Lab server:**
   ```bash
   jupyter lab --no-browser --ip=0.0.0.0 --port=8888
   ```
   - Server starts in 10-15 seconds
   - Access token will be displayed in output
   - Use Ctrl+C to stop server

3. **Test notebook execution:**
   ```bash
   # Test basic notebook
   jupyter nbconvert --execute --to python 00-python/basic/00-hello.ipynb --stdout
   
   # Test pandas notebook (in-place execution)
   jupyter nbconvert --execute --to notebook --inplace 00-python/pandas/01-pandas-series.ipynb
   ```

## Validation

### Required Validation Steps
**ALWAYS perform these steps after making any changes to notebooks or Python code:**

1. **Execute basic notebook test:**
   ```bash
   python3 -c "print('Hello, World!')"
   ```

2. **Execute pandas functionality test:**
   ```bash
   python3 -c "
   import pandas as pd
   import numpy as np
   # Create basic series
   s = pd.Series([1, 2, 3, 4])
   print('Series created:', s.sum())
   # Create basic dataframe
   df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
   print('DataFrame created:', df.shape)
   "
   ```

3. **Test at least one complete notebook from each section:**
   - Basic: `00-python/basic/00-hello.ipynb`
   - Pandas: `00-python/pandas/01-pandas-series.ipynb`
   - Advanced (if modifying submodules): Any notebook from `mcdia-python/Aulas/`

4. **Verify Jupyter server starts without errors:**
   ```bash
   timeout 30s jupyter lab --no-browser --ip=0.0.0.0 --port=8888 || echo "Server test completed"
   ```

### Manual Validation Scenarios
**After making changes to educational content, ALWAYS test these scenarios:**

1. **Student Experience Test**: Open a notebook, run all cells sequentially, verify outputs match expected learning outcomes
2. **Import Dependencies Test**: Verify all required imports work in a fresh Python session
3. **Data Files Test**: If working with data in `mcdia-python/data/`, verify file paths are correct and accessible

## Environment Details

- **Python Version**: 3.12.3+ (notebooks show 3.12.1 in metadata)
- **Key Dependencies**: pandas (2.3.2+), numpy (2.3.3+), jupyter
- **Notebook Kernel**: Python 3 (ipython3)
- **VS Code Setup**: Configured for conda environment management (see `.vscode/settings.json`)

## Common Tasks

### Working with Notebooks
- **View notebook content**: `str_replace_editor` with `.ipynb` files shows JSON structure
- **Execute notebook**: `jupyter nbconvert --execute --to [format] [notebook]`
- **Test all pandas notebooks**: Run notebooks 01-05 in `00-python/pandas/` directory

### Working with Submodules
- **Update submodules**: `git submodule update --remote`
- **Check submodule status**: `git submodule status`
- **Important**: Submodules contain course materials - avoid modifying unless specifically required

### Git Operations
- **Check repository status**: `git --no-pager status`
- **View differences**: `git --no-pager diff`
- **Commit changes**: Only use `report_progress` tool, not direct git commands

## Troubleshooting

### Common Issues and Solutions

1. **"pandas not available" error**:
   ```bash
   pip3 install pandas numpy jupyter
   ```

2. **Submodule clone failures**:
   - Switch to HTTPS URLs (commands provided in setup section)
   - Ensure network connectivity

3. **Jupyter server won't start**:
   - Check if port 8888 is in use
   - Try alternative port: `jupyter lab --port=8889`

4. **Notebook execution errors**:
   - Verify all required packages are installed
   - Check Python path and imports
   - Restart kernel if needed

## File Locations Reference

```
Repository Root: /home/runner/work/mcdia/mcdia/
├── .github/copilot-instructions.md (this file)
├── .vscode/settings.json (VS Code Python config)
├── 00-python/
│   ├── basic/00-hello.ipynb (Hello World)
│   └── pandas/ (6 tutorial notebooks)
├── mcdia-python/ (submodule - advanced courses)
└── mcdia-nivelamento/ (submodule - leveling courses)
```

### Frequently Used Commands Reference
```bash
# Repository status
ls -la

# Python verification
python3 --version
python3 -c "import pandas, numpy; print('Ready!')"

# Jupyter operations
jupyter lab --version
jupyter nbconvert --help

# Submodule operations  
git submodule status
git submodule update --init --recursive
```

**Remember**: This is an educational repository. Always test changes against the student learning experience and verify notebooks execute correctly with expected outputs.