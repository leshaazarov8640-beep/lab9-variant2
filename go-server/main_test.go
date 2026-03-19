package main

import (
    "bytes"
    "encoding/binary"
    "net/http"
    "net/http/httptest"
    "testing"
)

func TestProcessEndpoint(t *testing.T) {
    req := httptest.NewRequest("POST", "/process", bytes.NewReader([]byte{1, 2, 3, 4}))
    w := httptest.NewRecorder()
    
    handleProcess(w, req)
    
    resp := w.Result()
    if resp.StatusCode != http.StatusAccepted {
        t.Errorf("Expected status Accepted, got %v", resp.StatusCode)
    }
    
    if len(w.Body.Bytes()) != 8 {
        t.Errorf("Expected 8 bytes, got %d", len(w.Body.Bytes()))
    }
}

func TestResultEndpoint(t *testing.T) {
    req := httptest.NewRequest("POST", "/process", bytes.NewReader([]byte{1, 2, 3, 4}))
    w := httptest.NewRecorder()
    handleProcess(w, req)
    
    taskID := binary.LittleEndian.Uint64(w.Body.Bytes())
    
    req = httptest.NewRequest("GET", "/result?id="+string(rune(taskID)), nil)
    w = httptest.NewRecorder()
    handleResult(w, req)
}