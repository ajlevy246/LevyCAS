from .cli.main import main

if __name__ == "__main__":
    try:
        import textual
    except ImportError as Exception:
        raise ImportError("The LevyCAS TUI requires the 'Textual' package. Please see installation instructions in the README.")
        
    main()