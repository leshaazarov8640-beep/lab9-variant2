package main

import (
    "encoding/binary"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
    "os"
    "sync"
    "time"
)

type Task struct {
    ID        int
    Data      []byte
    CreatedAt time.Time
}

var taskQueue = make(chan Task, 100)
var taskCounter int
var mu sync.Mutex
var results = make(map[int][]byte)

func backgroundWorker() {
    for task := range taskQueue {
        log.Printf("Worker: processing task %d", task.ID)
        time.Sleep(2 * time.Second)
        
        processed := make([]byte, len(task.Data))
        for i, b := range task.Data {
            processed[i] = ^b
        }
        
        mu.Lock()
        results[task.ID] = processed
        mu.Unlock()
    }
}

type NumbersInput struct {
    Numbers []int `json:"numbers"`
}

type SumOutput struct {
    Sum int `json:"sum"`
}

func handleProcess(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodPost {
        http.Error(w, "Only POST allowed", http.StatusMethodNotAllowed)
        return
    }

    data, err := io.ReadAll(r.Body)
    if err != nil {
        http.Error(w, "Failed to read body", http.StatusBadRequest)
        return
    }
    defer r.Body.Close()

    mu.Lock()
    taskCounter++
    taskID := taskCounter
    mu.Unlock()

    taskQueue <- Task{
        ID:        taskID,
        Data:      data,
        CreatedAt: time.Now(),
    }

    response := make([]byte, 8)
    binary.LittleEndian.PutUint64(response, uint64(taskID))
    w.Header().Set("Content-Type", "application/octet-stream")
    w.WriteHeader(http.StatusAccepted)
    w.Write(response)
}

func handleResult(w http.ResponseWriter, r *http.Request) {
    if r.Method != http.MethodGet {
        http.Error(w, "Only GET allowed", http.StatusMethodNotAllowed)
        return
    }

    taskIDStr := r.URL.Query().Get("id")
    if taskIDStr == "" {
        http.Error(w, "Missing task ID", http.StatusBadRequest)
        return
    }

    var taskID int
    fmt.Sscanf(taskIDStr, "%d", &taskID)

    mu.Lock()
    result, exists := results[taskID]
    mu.Unlock()

    if !exists {
        http.Error(w, "Task not found or not completed", http.StatusNotFound)
        return
    }

    w.Header().Set("Content-Type", "application/octet-stream")
    w.Write(result)
}

func main() {
    stat, _ := os.Stdin.Stat()
    if (stat.Mode() & os.ModeCharDevice) == 0 {
        var input NumbersInput
        err := json.NewDecoder(os.Stdin).Decode(&input)
        if err != nil {
            log.Fatal("JSON decode error:", err)
        }

        sum := 0
        for _, n := range input.Numbers {
            sum += n * n
        }

        json.NewEncoder(os.Stdout).Encode(SumOutput{Sum: sum})
        return
    }

    go backgroundWorker()
    
    http.HandleFunc("/process", handleProcess)
    http.HandleFunc("/result", handleResult)
    
    log.Println("HTTP server starting on :8080")
    log.Fatal(http.ListenAndServe(":8080", nil))
}