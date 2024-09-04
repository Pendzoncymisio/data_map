from PyQt6.QtWidgets import QMenu, QInputDialog

class ContextMenu(QMenu):

    def __init__(self, caller, event):
        super().__init__()
        self.caller = caller

        #Create sub-menus
        add_node_menu = self.addMenu("Add Node")
        add_line_menu = self.addMenu("Add Line")

        add_source_action = add_node_menu.addAction("Add Source")
        add_sink_action = add_node_menu.addAction("Add Sink")
        add_line_to_action = add_line_menu.addAction("Add Line to")
        add_line_from_action = add_line_menu.addAction("Add Line from")

        # Add actions to the context menu
        expand_action = self.addAction("Expand")
        collapse_action = self.addAction("Collapse")
        
        set_group_action = self.addAction("Set group")
        change_icon_action = self.addAction("Change Icon")
        open_browser_action = self.addAction("Open in Browser")

        delete_menu = self.addMenu("Delete")
        delete_action = delete_menu.addAction("Confirm")

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
            new_source = caller.create_new_source()
            #TODO: Select newly created
        elif action == add_sink_action:
            new_sink = caller.create_new_sink()
            #TODO: Select newly created
        elif action == add_line_to_action:
            caller.add_line_to()
        elif action == add_line_from_action:
            caller.add_line_from()
        elif action == set_group_action:
            #TODO: Make this better for user by providing dropdown with existing group names
            group, ok = QInputDialog.getText(self, "Set Group", "Enter group name:")
            if ok:
                caller.set_group(group)
            else:
                print("Enter group name")
        elif action == change_icon_action:
            caller.context_change_icon()
        elif action == open_browser_action:
            caller.open_in_browser()
        elif action == delete_action:
            caller.delete()
