# SQLite Chat Session Persistence Feature

## Overview
The GitHub Repo AI Agent now includes persistent chat history using SQLite database. All conversations are automatically saved and restored when you return to a project.

## Features

### 1. Automatic Chat Saving
- Every message (user and assistant) is automatically saved to the database
- No manual action required - it happens in the background
- Each message is timestamped for tracking

### 2. Chat History Restoration
- When you select a project, all previous conversations are loaded
- Chat history persists across app restarts
- You can continue conversations from where you left off

### 3. Chat Statistics
- View total message count per project
- See when you last chatted with a project
- Statistics displayed in the Project Information expander

### 4. Clear Chat History
- New "🗑️ Clear Chat" button in the top right
- Clears all chat history for the current project
- Useful for starting fresh or removing old conversations

## Database Structure

### Table: `chat_sessions`
```sql
CREATE TABLE chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    role TEXT NOT NULL,              -- 'user' or 'assistant'
    content TEXT NOT NULL,            -- message content
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Database File
- Location: `chat_sessions.db` (root directory)
- Automatically created on first run
- Excluded from git via `.gitignore`

## Functions

### `init_database()`
- Initializes the SQLite database
- Creates the `chat_sessions` table if it doesn't exist
- Called automatically on app startup

### `save_message(project_name, role, content)`
- Saves a single message to the database
- Parameters:
  - `project_name`: Name of the project
  - `role`: 'user' or 'assistant'
  - `content`: Message text
- Called after each user message and AI response

### `load_chat_history(project_name)`
- Loads all chat messages for a project
- Returns list of messages ordered by timestamp
- Called when user selects a project

### `clear_chat_history(project_name)`
- Deletes all chat messages for a project
- Returns True on success, False on error
- Called when user clicks "Clear Chat" button

### `get_chat_stats(project_name)`
- Returns statistics about chat history
- Returns:
  - `total_messages`: Total message count
  - `first_message`: Timestamp of first message
  - `last_message`: Timestamp of last message

## User Interface Changes

### Project Information Expander
- Added 4th column for chat statistics
- Shows "Chat Messages" count
- Shows "Last Chat" date

### Top Action Bar
- Added "🗑️ Clear Chat" button
- Positioned next to "📄 Generate Report" button
- Confirms action with success message

### Project Selection
- Automatically loads chat history when switching projects
- Seamless transition between projects

## Usage Examples

### Starting a New Conversation
1. Select a project from the sidebar
2. Previous chat history loads automatically
3. Continue the conversation or start a new topic

### Clearing Chat History
1. Click "🗑️ Clear Chat" button
2. Confirm the action
3. Chat history is cleared, start fresh

### Viewing Chat Statistics
1. Expand "📊 Project Information"
2. Check the 4th column for chat stats
3. See total messages and last chat date

## Benefits

1. **Continuity**: Pick up conversations where you left off
2. **Context**: Review previous discussions about the codebase
3. **History**: Track your analysis journey over time
4. **Persistence**: Never lose important insights
5. **Organization**: Separate chat history per project

## Technical Details

### Database Location
- File: `chat_sessions.db`
- Format: SQLite3
- Size: Grows with chat history (typically small)

### Performance
- Fast read/write operations
- Indexed by project_name for quick queries
- Minimal overhead on chat operations

### Data Privacy
- Database stored locally
- Not included in git repository
- Can be deleted manually if needed

### Compatibility
- Works with Streamlit Cloud
- No additional dependencies required
- SQLite is built into Python

## Troubleshooting

### Chat History Not Loading
- Check if `chat_sessions.db` exists
- Verify database permissions
- Check console for error messages

### Database Errors
- Delete `chat_sessions.db` to reset
- Database will be recreated automatically
- Previous chat history will be lost

### Performance Issues
- Large chat histories may slow down loading
- Use "Clear Chat" to remove old conversations
- Consider archiving old projects

## Future Enhancements

Potential improvements:
- Export chat history to text/markdown
- Search within chat history
- Filter messages by date range
- Archive old conversations
- Import/export chat sessions
- Chat history analytics

## Migration Notes

### From Previous Version
- No migration needed
- Old sessions in `st.session_state` are not preserved
- New chats will be saved automatically

### Backup Recommendations
- Backup `chat_sessions.db` periodically
- Include in your backup strategy
- Can be copied to other machines

## Summary

The SQLite chat persistence feature ensures your conversations with the AI agent are never lost. It provides a seamless experience across sessions while maintaining performance and simplicity.
