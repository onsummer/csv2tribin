# 简介

该 python 脚本是从 csv 转换到特制二进制三角网数据的工具，对 csv 数据有要求，已精简到只需两个参数即可生成。

见 [用法](#用法) 和 [文档](#文档)

# 1 数据转换过程

\- csv 
→ 点shp (步骤1)
→ tin数据集 (步骤2)
→ 三角形面shp (步骤3) 
→ 筛选范围后的三角形面shp (步骤4)
→ 二进制化成bin文件并gzip压缩 (步骤5)

## 注意事项

对 csv 和覆盖面数据有要求，其坐标系统需为 `EPSG:4326`

# 2 依赖环境

ArcMap 内置的 arcpy

# 3 需要输入的数据

- 有经纬度、高度三列数值的 csv 数据，例如
- 范围多边形shp

# 4 用法

参考 test.py 中的写法，调用 run 函数即可

## run 函数

### 参数

- `csv_dir`: csv 数据文件路径，请使用绝对路径
- `coverage_layer_shppath`: 覆盖图层 shp 文件绝对路径
- `result_dir`?: 结果路径，使用绝对路径，若不指定则使用 csv_dir
- `is_clean_temp`?: 布尔值，是否删除中间步骤文件，默认删除；有可能会被 arcpy 占用一部分文件，需要程序运行结束后手动删除
- `csv_filter`?: csv 数据文件后缀名，默认 '*.csv'
- `open_onend`?: 布尔值，指示运行结束后是否打开结果文件夹，默认不打开
- `skip`?: 数字 list，指示需要跳过计算的步骤，例如要跳过 1、2、3 步，只需传递 `[1, 2, 3]` 即可，默认不跳过，即 `None`；跳步请注意中间步骤所需数据的完整性、对应中间步骤的文件存在
步骤1~5会在 `result_dir` 生成如下命名的文件夹：
  - 步骤1: `to_ptshp`
  - 步骤2: `tins`
  - 步骤3: `triangles_shp`
  - 步骤4: `filtered_triangles`
  - 步骤5: `finally_result`

``` py
from csv2tribin import run

run(
  r'C:\Users\CDCI\Desktop\pytest', 
  r'C:\Users\CDCI\Desktop\1-FullDomain\coverage.shp', 
  None,
  False,
  '*.txt',
  True
)
```

# 5 文档

## ① 子模块 `csv2tribin.data_io`

### a. 函数 `gz_compress`

#### 用途

使用 `gzip` 压缩某个文件，在其相同路径下生成同名的 gz 后缀压缩文件。

#### 参数

- `path`：字符串类型，文件的绝对路径。

#### 举例

``` py
from util.data_io import *

gz_compress(r'C:\a.txt') # 生成 C:\a.txt.gz
```

### b. 函数 `delete_dir`

#### 用途

递归删除文件夹。

#### 参数

- `dirs`: 不定参数，可传递 1~N 个字符串，为需要删除的文件夹的绝对路径

#### 举例

``` py
from util.data_io import *

delete_dir(r'D:\a') # 删除一个
delete_dir(r'D:\b', r'D:\c') # 删除两个
```

### c. 函数 `bin2gz`

#### 用途

压缩一系列文件。

#### 参数

- `files`: 一个 list，每个元素是字符串，是待压缩文件的绝对路径

#### 举例

``` py
from util.data_io import *

bin2gz([r'D:\a.json', r'D:\b.json'])
# 生成 D:\a.json.gz 和 D:\b.json.gz
```

## ② 子模块 `csv2tribin.data_utils`

### a. 函数 `parse_csv_to_pointshp`

#### 用途

转换csv文件到点文件，csv 文件需要有 3 列数值列，依次为经度、纬度、高度。
csv 文件要使用 utf-8 编码。

#### 参数

- `csvfiles`: 字符串 list，csv 文件的绝对路径
- `result_dir`: 字符串，输出点 shp 到哪个文件夹

#### 举例

``` py
from csv2tribin.data_utils import *

parse_csv_to_pointshp(
  [r'D:\01.csv', r'D:\02.csv'],
  r'D:\result'
)
```

### b. 函数 `pointshp_to_tin`

#### 用途

点 shp 转不规则三角网，需要有名为 `zvalue` 的数值字段

#### 参数

- `shp_files`: 字符串 list，shp文件路径数组，要绝对路径
- `result_dir`: 字符串，输出 tin 数据集到哪个文件夹，用绝对路径

#### 举例

``` py
from csv2tribin.data_utils import *

pointshp_to_tin(
  [r'D:\pt01.shp', r'D:\pt02.shp'],
  r'D:\result'
)
```

### c. 函数 `tin_to_triangle`

#### 用途

不规则三角网数据集转三角形面 shp

#### 参数

- `tins`: 字符串 list，不规则三角网数据集路径数组，使用绝对路径
- `result_dir`: 字符串，输出三角形面到哪个文件夹，使用绝对路径

#### 举例

``` py
from csv2tribin.data_utils import *

tin_to_triangle(
  [r'D:\tins\a01', r'D:\tins\a02'],
  r'D:\result'
)
```

### d. 函数 `filter_triangle`

#### 用途

空间选择。使用一个面要素或面 shp 选择生成的三角形面

#### 参数

- `triangles_shps`: 字符串 list，三角形 shp 面数据路径数组，要求是绝对路径
- `coverage_layer`: 字符串，一个 shp 文件绝对路径，作为空间选择的覆盖区域
- `result_dir`: 字符串，输出空间选择后的三角形面数据到哪个文件夹

#### 举例

``` py
from csv2tribin.data_utils import *

filter_triangle(
  [r'D:\triangle01.shp', r'D:triangle02.shp'],
  r'D:\coverage_layer.shp',
  r'D:\result'
)
```

### e. 函数 `geometry_to_binfile`

#### 用途

shp 中的几何数据转到二进制 VBO

#### 参数

- `shp_names`：字符串 list，每个元素是 shp 文件的绝对路径
- `result_dir`：字符串，输出二进制文件到什么地方，使用绝对路径
- `is_compress`：布尔值，是否顺便使用 gzip 压缩

#### 举例

``` py
from csv2tribin.data_utils import *

geometry_to_binfile(
  [r'D:\a01.shp', r'D:\a02.shp'],
  r'D:\result',
  True
)
```

会在 `D:\result` 中生成 `a01.bin`、`a02.bin`、`a01.txt`、`a02.txt`、`a01.bin.gz`、`a02.bin.gz` 和 `namelist.json` 文件。
其中，`bin` 文件是提取出来的图形二进制数据，`txt` 是高度值的最大最小值统计数据，`bin.gz` 是 bin 文件 gzip 压缩后的文件。

# 5 测试情况

- parse_csv_to_pointshp 测试通过
- pointshp_to_tin 测试通过
- tin_to_triangle 测试通过
- filter_triangle 测试通过
- geometry_to_binfile 测试通过
- 全体测试：通过