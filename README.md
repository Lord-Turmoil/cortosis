# Code: Cortosis

## Configuration

The configuration file should be placed in the root directory of the project, by default is `config.yaml`. You can see `test/conversation_test.py` for example.

```yaml
llm:
  select: qianwen  # profile name
  profiles:
    - name: qianwen
      base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
      key: sk-*********************
    - name: local
      base_url: http://127.0.0.1:8000/v1
      key: key-*************
```

To run the test, you can use the following command:

```bash
python test/conversation_test.py
```
