import subprocess
import json
import os

def test_go_subprocess_json():
    """Тест задания 4: JSON через stdin/stdout"""
    go_exe = os.path.abspath("../go-server/go-server.exe")
    
    proc = subprocess.Popen(
        [go_exe],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    input_data = json.dumps({"numbers": [1, 2, 3, 4, 5]}).encode()
    output, error = proc.communicate(input_data)
    
    if error:
        print(f"Go error: {error.decode()}")
    
    result = json.loads(output)
    assert result["sum"] == 55
    print("✅ JSON subprocess test passed")

if __name__ == "__main__":
    test_go_subprocess_json()