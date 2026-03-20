package main

import (
    "bytes"
    "encoding/binary"
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestProcessEndpoint(t *testing.T) {
    testData := []byte{10, 20, 30}
    req := httptest.NewRequest("POST", "/process", bytes.NewReader(testData))
    w := httptest.NewRecorder()
    
    handleProcess(w, req)
    
    if w.Code != http.StatusAccepted {
        t.Errorf("Expected 202, got %d", w.Code)
    }
    
    if len(w.Body.Bytes()) != 8 {
        t.Errorf("Expected 8 bytes, got %d", len(w.Body.Bytes()))
    }
}

func TestResultEndpoint(t *testing.T) {
    // Сначала создаем задачу
    testData := []byte{1, 2, 3}
    req := httptest.NewRequest("POST", "/process", bytes.NewReader(testData))
    w := httptest.NewRecorder()
    handleProcess(w, req)
    
    taskID := binary.LittleEndian.Uint64(w.Body.Bytes())
    
    // Пытаемся получить результат (должен быть 404, т.к. еще не обработан)
    req = httptest.NewRequest("GET", "/result?id="+string(rune(taskID)), nil)
    w = httptest.NewRecorder()
    handleResult(w, req)
    
    if w.Code != http.StatusNotFound {
        t.Errorf("Expected 404, got %d", w.Code)
    }
}

func TestJSONMode(t *testing.T) {
    // Сохраняем оригинальные os.Stdin и os.Stdout
    oldStdin := os.Stdin
    oldStdout := os.Stdout
    defer func() {
        os.Stdin = oldStdin
        os.Stdout = oldStdout
    }()
    
    // Создаем pipe для имитации stdin
    r, w, _ := os.Pipe()
    os.Stdin = r
    
    // Записываем JSON в pipe
    input := `{"numbers":[1,2,3,4,5]}`
    w.Write([]byte(input))
    w.Close()
    
    // Захватываем stdout
    outR, outW, _ := os.Pipe()
    os.Stdout = outW
    
    // Запускаем main в режиме подпроцесса
    go func() {
        main()
    }()
    
    // Читаем результат
    outW.Close()
    buf := new(bytes.Buffer)
    buf.ReadFrom(outR)
    
    var result SumOutput
    json.Unmarshal(buf.Bytes(), &result)
    
    if result.Sum != 55 {
        t.Errorf("Expected 55, got %d", result.Sum)
    }
}