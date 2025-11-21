"""
Stub module to provide BaseTool to the crewai runtime without importing the full crewai_tools package.
This allows the application to avoid the dependency on the heavy crewai_tools distribution that requires
`crewai.tools.BaseTool`, which is not available in the current crewai release.
"""

from __future__ import annotations

from typing import Any


class BaseTool:
    """Minimal placeholder so imports succeed when crewai.inside_agent tries to import BaseTool."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.name = kwargs.get("name") or (args[0] if args else "base-tool")
        self.description = kwargs.get("description", "")

    def to_langchain(self) -> Any:
        """Provide a minimal object that mimics the LangChain tool interface."""
        name = self.name
        description = self.description

        class _DummyLangChainTool:
            def __init__(self) -> None:
                self.name = name
                self.description = description

            def __call__(self, *args: Any, **kwargs: Any) -> None:
                return None

        return _DummyLangChainTool()


