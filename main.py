import os
import sys
import shutil
import tempfile
import hashlib

def get_entry_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'entry.png')

def main():
    source = get_entry_path()
    if not os.path.exists(source):
        print(f"Error: {source} missing", file=sys.stderr)
        sys.exit(1)

    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    destination = os.path.join(output_dir, 'entry.png')

    source_size = os.path.getsize(source)

    # Atomic copy
    fd, staged = tempfile.mkstemp(dir=output_dir)
    try:
        with open(source, 'rb') as f_src:
            with os.fdopen(fd, 'wb') as f_dst:
                shutil.copyfileobj(f_src, f_dst)

        # Verify
        if os.path.getsize(staged) != source_size:
            print("Error: Size mismatch", file=sys.stderr)
            os.remove(staged)
            sys.exit(1)

        # Make world readable
        os.chmod(staged, 0o644)

        # Replace
        os.replace(staged, destination)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if os.path.exists(staged):
            os.remove(staged)
        sys.exit(1)

    print(f"Deployed {destination}")

if __name__ == '__main__':
    main()
