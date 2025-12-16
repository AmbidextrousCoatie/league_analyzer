# Database Switching System Guide

## Overview

The new database switching system provides a reliable, session-based approach to switching between different data sources in the League Analyzer application. This system addresses the instability issues that occurred in production environments.

## Key Features

### 1. **Session-Based State Management**
- Database selection is persisted in Flask sessions
- Survives server restarts and worker process changes
- User-specific database preferences

### 2. **Robust Error Handling**
- Automatic rollback on failed database switches
- Graceful fallback to default data source
- Comprehensive error logging and user notifications

### 3. **Race Condition Prevention**
- Prevents multiple simultaneous database switch requests
- Loading states and UI feedback
- Request deduplication

### 4. **Centralized Configuration**
- All data sources configured in one place
- Easy to add new data sources
- Validation of data source availability

## Architecture

### Components

#### 1. **DatabaseConfig** (`app/config/database_config.py`)
- Centralized configuration management
- Data source validation and metadata
- Default source management

#### 2. **DataManager** (`app/services/data_manager.py`)
- Session-based state persistence
- Error handling and rollback logic
- Server instance refresh coordination

#### 3. **DatabaseSelector** (`app/templates/components/database_selector.html`)
- Modern UI component with loading states
- Real-time feedback and notifications
- Event-driven architecture

#### 4. **API Routes** (`app/routes/main.py`)
- RESTful endpoints for database operations
- Comprehensive error responses
- Detailed source information

## Usage

### For Users

1. **Switching Databases**
   - Click the database selector in the navbar
   - Choose from available data sources
   - Wait for confirmation of successful switch

2. **Visual Feedback**
   - Loading spinner during switch
   - Success/error notifications
   - Current database display

### For Developers

#### Adding a New Data Source

1. **Update Configuration**
   ```python
   # In app/config/database_config.py
   'new_data_source.csv': DataSourceConfig(
       filename='new_data_source.csv',
       display_name='New Data Source',
       description='Description of the new data source',
       is_default=False,
       is_enabled=True
   )
   ```

2. **Place Data File**
   - Add CSV file to `database/data/` directory
   - Ensure proper formatting (semicolon-separated)

3. **Test the Integration**
   - Visit `/database-test` to verify functionality
   - Check server logs for any errors

#### API Endpoints

- `GET /get-data-sources-info` - Get detailed information about all sources
- `GET /get-data-source` - Get current data source information
- `GET /reload-data?source=<filename>` - Switch to specified data source
- `GET /data-source-changed` - Get notification of data source changes

## Troubleshooting

### Common Issues

#### 1. **Database Switch Fails**
- Check if data file exists in `database/data/`
- Verify file permissions
- Check server logs for detailed error messages

#### 2. **Session Issues**
- Ensure Flask session configuration is correct
- Check if session storage is working in production
- Verify session secret key is set

#### 3. **UI Not Updating**
- Check browser console for JavaScript errors
- Verify network requests are completing
- Ensure Bootstrap CSS/JS is loaded

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export FLASK_DEBUG=1
```

### Test Page

Visit `/database-test` to:
- View current database information
- See available data sources
- Test database switching functionality
- Verify data loading

## Production Deployment

### Requirements

1. **Session Storage**
   - Configure Flask session storage (Redis recommended for production)
   - Set secure session secret key

2. **File Permissions**
   - Ensure web server can read data files
   - Set appropriate file permissions

3. **Error Monitoring**
   - Monitor application logs for database switch errors
   - Set up alerts for failed switches

### Configuration

```python
# Production session configuration
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
app.config['SECRET_KEY'] = 'your-secure-secret-key'
```

## Migration from Old System

The new system is backward compatible. Existing code will continue to work, but benefits from:

- More reliable database switching
- Better error handling
- Improved user experience
- Session persistence

### Breaking Changes

None - the new system is a drop-in replacement that maintains the same API surface.

## Performance Considerations

- Database switches are cached in memory
- Session data is lightweight
- UI updates are asynchronous
- Minimal impact on application performance

## Security

- Data source validation prevents path traversal
- Session-based isolation between users
- No sensitive data in client-side code
- Input sanitization on all endpoints 