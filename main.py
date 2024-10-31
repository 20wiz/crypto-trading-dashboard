[Previous content of main.py up to line 255]
                    if st.button("➖ Zoom Out"):
                        y_min = float(data['low'].min() * 0.95)  # Changed from 0.9
                        y_max = float(data['high'].max() * 1.05)  # Changed from 1.1
                        st.session_state.y_axis_range = (y_min, y_max)
                with zoom_col2:
                    if st.button("➕ Zoom In"):
                        y_min = float(data['low'].min() * 0.98)  # Changed from 0.97
                        y_max = float(data['high'].max() * 1.02)  # Changed from 1.03
                        st.session_state.y_axis_range = (y_min, y_max)
[Rest of main.py content remains the same]
