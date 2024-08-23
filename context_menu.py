from PyQt6.QtWidgets import QMenu

class ContextMenu(QMenu):

    def __init__(self, caller, event):
        super().__init__()
        self.caller = caller

        # Add actions to the context menu
        expand_action = self.addAction("Expand")
        collapse_action = self.addAction("Collapse")
        add_source_action = self.addAction("Add Source")
        add_sink_action = self.addAction("Add Sink")
        change_icon_action = self.addAction("Change Icon")
        open_browser_action = self.addAction("Open in Browser")

        expand_action.setEnabled(caller.expandable)
        collapse_action.setEnabled(caller.group)

        # Show the context menu at the current mouse position
        action = self.exec(event.screenPos())

        # Handle the selected action
        if action == expand_action:
            caller.expand()
        elif action == collapse_action:
            caller.collapse()
        elif action == add_source_action:
            caller.create_new_source()
        elif action == add_sink_action:
            caller.create_new_sink()
        elif action == change_icon_action:
            caller.context_change_icon()
        elif action == open_browser_action:
            caller.open_in_browser()
