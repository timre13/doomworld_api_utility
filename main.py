import requests
import json
import typing as t
import pygments
from pygments import lexers, formatters

def prettifyJson(arg: t.Any):
    out = json.dumps(arg, indent=2, ensure_ascii=False)
    out = pygments.highlight(out, lexers.JsonLexer(), formatters.Terminal256Formatter(style="monokai"))
    return out

def logJson(arg: t.Any):
    print(prettifyJson(arg))

class ApiErrorOrWarning:
    def __init__(self, isError: bool, type: t.Any, message: t.Any):
        self.isError = isError
        self.type = type
        self.message = message

    @classmethod
    def fromJson(cls, isError: bool, value: dict):
        return cls(isError, value["type"], value["message"])

    def __str__(self) -> str:
        return f"[{'Error' if self.isError else 'Warning'}: {self.type}; {self.message}]"


class ApiResponse:
    def __init__(self,
                 version: int,
                 content: t.Any | None,
                 error: ApiErrorOrWarning | None,
                 warning: ApiErrorOrWarning | None
                 ):
        assert isinstance(version, int)
        self.version = version
        self.content = content
        assert isinstance(error, ApiErrorOrWarning) or (error is None)
        self.error = error
        assert isinstance(warning, ApiErrorOrWarning) or (warning is None)
        self.warning = warning

def makeApiCall(action: str, **kwargs) -> ApiResponse:
    url = f"https://doomworld.com/idgames/api/api.php?action={action}&out=json"
    for k, v in kwargs.items():
        url += f"&{k}={v}"
    print(f"Making request to \"{url}\"")
    response: dict[str, t.Any] = json.loads(requests.get(url).content.decode())
    return ApiResponse(response["meta"]["version"],
                       response.get("content", None),
                       ApiErrorOrWarning.fromJson(True, response["error"]) if "error" in response.keys() else None,
                       ApiErrorOrWarning.fromJson(False, response["warning"]) if "warning" in response.keys() else None,
                       )

logJson(makeApiCall("about").content)
logJson(makeApiCall("get", id=18748).content)
result = makeApiCall("search", query="btsx")
logJson(result.content)
print(result.error)
print(result.warning)
result = makeApiCall("search", query="asdfasdfasdfasdf")
logJson(result.content)
print(result.error)
print(result.warning)
