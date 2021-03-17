# Map creator and editor for Space Sodomy 2 Online
This python based app create a map using polygons. Output file has walls, walls has points and other info.

### How to make new polygon
To create new point you can use **mouse left click** on canvas. This point will automatically append to current new polygon (red coloured).

Use **mouse right click** to save your current polygon. Saved polygons are black.

To move on canvas you can use **Left/Right/Up/Down** keys.

To change scale you can use **mouse wheel**.

Also you can change inner/outer wall by clicking on buttons. Default walls will be outer.

### File system
Saving your map binded to **Ctrl+S**.
First, type file name in text field below. Then, use  **Ctrl+S**.

Opening saved maps binded to  **Ctrl+O**.
First, type file name in text field below. Then, use  **Ctrl+O**.

Start new map binded to  **Ctrl+N**.

### Other commands
To undo you can use **Ctrl+Z**.

To close program you can use **Ctrl+W**.

To enter command you can use **Ctrl+R**.
Type command in text field and press **Ctrl+R**.

Well, there are only three commands: 
1. **Scale**
Type "scale 10". It will change scale on canvas to 10

2. **Camera x/y**
Type "cam_x 100". It will change camera x coordinate on canvas to 100
Type "cam_y 100". It will change camera y coordinate on canvas to 100

3. **Delete current polygon**
Type "del_now". It will destroy red polygon. 
