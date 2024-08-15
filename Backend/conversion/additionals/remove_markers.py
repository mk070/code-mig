def remove_code_markers(response: str) -> str:
    markers = ["```python", "```csharp", "```java", "```pyspark", "```cobol", "```.net", "```c", "```json", "```"]

    # Check if the response starts and ends with any of the markers
    for marker in markers:
        if response.startswith(marker):
            response = response[len(marker):].lstrip()  # Remove the marker and leading whitespace
        if response.endswith(marker):
            response = response[:-len(marker)].rstrip()  # Remove the marker and trailing whitespace

    return response