# Редактор карт для игры SS 2 Online
Это приложение, написанное на питоне, создает карту из полигонов. В файл вывода записываются стены, их точки и другая информация. Примерная занятость оперативной памяти: от 6 МБ.
Чтобы запустить приложение воспользуйтесь интерпретатором **python 3.8 PyCharm** или **скачайте zip архив, распакуйте куда угодно и запустите SS2 Map Editor.exe**.

Сам архив: https://github.com/lvlcnapps/ss2_map_editor/raw/master/SS2_map_editor_beta/SS2%20map%20editor.zip

Код: https://github.com/lvlcnapps/ss2_map_editor/blob/master/SS2_map_editor_beta/venv/main.py

### GUI
Не пугайтесь интерфейса, я просто криворукий в верстке. Итак, разберемся: перед Вами открытое приложение, что же там есть.
1) **Заголовок**. Сначала там только название приложения. При сохранении/открытии карт там будет небольшая информация о рабочем файле.
2) **Текст**. При запуске там будет надпись *Начало работы*, как только мышь зайдет на холст, там появится другой текст, информирующий о координатах мыши и масштабе холста.
3) **Холст**. На холсте можно рисовать стены-полигоны. Конечно, сначала там нет полигонов, но зато есть сетка. Оси координат x и y отмечены синими линиями.
4) **Кнопки**. Кнопками можно выбрать тип коллизии создающейся стены, как только Вы сохраните стену, изменить её тип будет нельзя. По умолчанию - внешняя коллизия.
5) **Текстовое поле**. Универсальный помощник для сохранения и загрузки карт и ориентирования в проекте. Подробнее о файловой системе и командах ниже.
6) **Снова кнопки**. Кнопки для работы с проектом. Введите название файла и жмите кнопки.

### Как создать новый полигон
Для создания точки нажмите **левой клавишей мыши** *(далее ЛКМ и правая клавиша - ПКМ)* на холсте. Это точка автоматически добавится к создающемся полигону *(он красного цвета)*.

Жмите **ПКМ**, чтобы сохранить красный полигон. Он присоединится к остальным, уже созданным полигонам и станет черного цвета.
Если нажать **ПКМ** по черному полигону, то он будет в режиме *"выбранного"*, такие полигоны можно удалять, нажимая **Delete**

Для передвижения по холсту используйте **нажатие колесика мыши** *(кручение колесика - масштаб, чтобы перемещать холст нужно жать колесико и двигать мышь)*

Для смены масштаба крутите **колёсико мыши**

Также, можно менять тип стены кнопками ниже холста прямо во время создания красного полигона. От этого зависит **коллизия внутри стен или снаружи**. По умолчанию стены внешней коллизии.

### Файловая система
Какой это был бы редактор без сохранения и загрузки карт. Да, можно даже загрузить какую то старую карту (карты из SS1 не поддерживаются) и дополнить её. Возможно потом и удаление полигонов сделаю для полноты редактирования.

Чтобы сохранить карту жмите **Ctrl+S** *(в английской раскладке)*.
Для начала, напишите **будущее название файла** без расширения в текстовом поле, а потом уже сохраняйте комбинацией клавиш, иначе карта сохранится в default_name.lvl

Чтобы открыть файл с картой жмите **Ctrl+O** *(в английской раскладке)*.
Для начала, напишите **название файла** без расширения в текстовом поле, а потом уже открывайте комбинацией клавиш, иначе не откроется.

Чтобы начать с нуля жмите **Ctrl+N** *(в английской раскладке)*. Сохранить старый проект не предложит, так что аккуратнее.

### Горячие клавиши

Чтобы отменить создание прошлого черного полигона, жмите **Ctrl+Z** *(в английской раскладке)*. Но аккуратно, работает нестабильно.

Чтобы закрыть приложение используйте **Ctrl+W** *(в английской раскладке)* *(не предложит сохраниться)*.

Может возникнуть ситуация, что колесико мыши не спасает, стрелочки тоже, из-за этого неудобно рисовать. Задать масштаб холста и положение камеры можно командами.
Сначала напишите команду из списка ниже, потом жмите **Ctrl+R** *(в английской раскладке)*.

Пасхалка-помощь на F1
