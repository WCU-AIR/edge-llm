## Running `llama.cpp` locally on Mac

### 1. Add gguf model to models/
ex. qwen2.5-1.5b-instruct-q4_k_m.gguf

### 2. Build `llama.cpp`

From the root directory run:

```
cd third_party/llama.cpp &&
mkdir -p build &&
cd build &&
cmake .. -DLLAMA_BUILD_SERVER=OFF &&
cmake --build . -j
```

### 3. Run chat
continuous:
`./bin/llama-simple-chat -m ../../../models/qwen2.5-1.5b-instruct-q4_k_m.gguf`


This will run locally in your terminal. No server is created