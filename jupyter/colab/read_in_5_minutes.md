[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/MS-Quality-hub/pymzqc/blob/v1.0.0rc1/jupyter/colab/read_in_5_minutes.ipynb)

# Welcome to the 5-Minute mzQC interactive guides with python!
This python notebook will guide you through your first steps with reading someone's mzQC in python. 

First we will explore how to open and read a `mzQC` file, explore its' content and dataframe integration, and finally visualise a metric for interactive view in colab! (We assume it is not the first time you get your feet wet with python, otherwise rather plan for 25 minutes.)

## Setting the scene
First, we need to install the mzQC python library. When outside of the python notebook, find out [here](https://github.com/MS-Quality-hub/pymzqc) how to install locally (spoiler: usually just `pip install pymzqc`).


```python
#@title This will install the latest version of pymzqc
%pip install pymzqc --quiet
```

Then, we load this right into our python session by loading pymzqc (`from mzqc`). We'll also utilise some other libraries, too.
For example, we will use `requests` to load some data from the web. 



```python
from mzqc import MZQCFile as qc
import pandas as pd
from io import StringIO
import requests
import plotly.express as px
```

# Acquire data
Next, we need to acquire some data.
For this notebook you have two choices.
1. [either](#local-file-cell-id) upload a file from your local disk
2. [or](#github-file-cell-id) load an example file from the mzQC GitHub repo

<a name="local-file-cell-id"></a>
## Option 1.
Select and upload a local file here!


```python
#@title Upload `.mzQC` file here!
from google.colab import files
try:
  uploaded = files.upload()
except:
  print("If that does not work, proceed with option 2.")

# maybe an alternative?
# from google.colab import drive
# drive.mount('/content/drive')
```



<input type="file" id="files-ea0849e7-b72e-4e97-a3a1-ebddc4907a7a" name="files[]" multiple disabled
   style="border:none" />
<output id="result-ea0849e7-b72e-4e97-a3a1-ebddc4907a7a">
 Upload widget is only available when the cell has been executed in the
 current browser session. Please rerun this cell to enable.
 </output>
 <script src="/nbextensions/google.colab/files.js"></script> 


    If that does not work, proceed with option 2.


And load it as `JsonSerialisable` from file:


```python
#@title Provide a file object by `open` either a colab uploaded file or a file path if you are using this notebook locally.
with open(uploaded['filename.mzQC'], "r") as file:
  some_mzqc = qc.JsonSerialisable.FromJson(file)
```

<a name="github-file-cell-id"></a>
## Option 2.
Load a file from GitHub


```python
#@title Loading files from the web works only a little different.
response = requests.get('https://github.com/HUPO-PSI/mzQC/raw/main/doc/examples/metabo-batches.mzQC')
some_mzqc = qc.JsonSerialisable.FromJson(response.text)
```

# Inspect data
We can now go ahead and take a look what that file we loaded has on offer:


```python
print(some_mzqc.description)
```

    This dataset is based on the analysis of polar extracts from a nucleotype-plasmotype combination study of Arabidopsis for 58 different genotypes. For details of the used plant material we refer to Flood (2015). Analysis of the polar, derivatized metabolites by GC-ToF-MS (Agilent 6890 GC coupled to a Leco Pegasus III MS) and processing of the data were done as described in Villafort Carvalho et al. (2015). Here, the number of metabolites (75) is much lower than in the other two data sets, partly because the focus was on the primary rather than the secondary metabolites. The number of samples was 240, with a percentage of non-detects of 16 %; the maximum fraction of non-detects in individual metabolites is 92 %. All metabolites were retained in the analysis. Four batches of 31-89 samples were employed, containing 2-6 QCs per batch, 14 in total.


**pymzqc** deserialised JSON arrays (i.e. the `runQualities` and their `qualityMetrics`) can be used like python lists:


```python
for m in some_mzqc.runQualities[0].qualityMetrics:
    print(m.name)
```

    Detected Compounds


You can traverse the hierarchy with standard python member access notation (`.`) and get to the bottom of things (like a metric `name` or `value`).


```python
some_mzqc.runQualities[0].qualityMetrics[0].value

```




    57



We can also get the table metrics directly as pandas dataframe! 🤯


```python
from google.colab import data_table
data_table.enable_dataframe_formatter()

df = pd.DataFrame(some_mzqc.setQualities[0].qualityMetrics[0].value)
df
```





  <div id="df-e8f5977c-fb29-4912-8ee3-8d3b8148a65d">
    <div class="colab-df-container">
      <div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Run name</th>
      <th>PCA Dimension 1</th>
      <th>PCA Dimension 2</th>
      <th>PCA Dimension 3</th>
      <th>PCA Dimension 4</th>
      <th>PCA Dimension 5</th>
      <th>Injection sequence number</th>
      <th>Batch label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>GCMS ToF sample 10</td>
      <td>-3.348963</td>
      <td>-2.341435</td>
      <td>-1.486755</td>
      <td>-0.276620</td>
      <td>-2.683632</td>
      <td>13</td>
      <td>4</td>
    </tr>
    <tr>
      <th>1</th>
      <td>GCMS ToF sample 100</td>
      <td>0.419126</td>
      <td>2.055220</td>
      <td>-0.396590</td>
      <td>1.780880</td>
      <td>-2.020238</td>
      <td>16</td>
      <td>7</td>
    </tr>
    <tr>
      <th>2</th>
      <td>GCMS ToF sample 101</td>
      <td>6.824155</td>
      <td>1.514235</td>
      <td>1.163668</td>
      <td>0.173623</td>
      <td>-3.088806</td>
      <td>17</td>
      <td>7</td>
    </tr>
    <tr>
      <th>3</th>
      <td>GCMS ToF sample 102</td>
      <td>-1.080886</td>
      <td>2.994551</td>
      <td>0.421837</td>
      <td>0.013869</td>
      <td>-3.161503</td>
      <td>18</td>
      <td>7</td>
    </tr>
    <tr>
      <th>4</th>
      <td>GCMS ToF sample 103</td>
      <td>-1.707045</td>
      <td>6.070161</td>
      <td>0.627950</td>
      <td>-0.628732</td>
      <td>-1.064512</td>
      <td>19</td>
      <td>7</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>221</th>
      <td>GCMS ToF sample 95</td>
      <td>4.246444</td>
      <td>1.841355</td>
      <td>0.670941</td>
      <td>0.938284</td>
      <td>-1.520605</td>
      <td>11</td>
      <td>7</td>
    </tr>
    <tr>
      <th>222</th>
      <td>GCMS ToF sample 96</td>
      <td>2.368072</td>
      <td>1.001514</td>
      <td>1.235160</td>
      <td>-0.091535</td>
      <td>-3.000758</td>
      <td>12</td>
      <td>7</td>
    </tr>
    <tr>
      <th>223</th>
      <td>GCMS ToF sample 97</td>
      <td>1.674060</td>
      <td>0.450211</td>
      <td>-0.512383</td>
      <td>2.100324</td>
      <td>-1.654505</td>
      <td>13</td>
      <td>7</td>
    </tr>
    <tr>
      <th>224</th>
      <td>GCMS ToF sample 98</td>
      <td>-2.928426</td>
      <td>4.175587</td>
      <td>-0.449582</td>
      <td>0.333712</td>
      <td>-0.814875</td>
      <td>14</td>
      <td>7</td>
    </tr>
    <tr>
      <th>225</th>
      <td>GCMS ToF sample 99</td>
      <td>10.000164</td>
      <td>1.918147</td>
      <td>-1.348393</td>
      <td>0.275859</td>
      <td>0.749887</td>
      <td>15</td>
      <td>7</td>
    </tr>
  </tbody>
</table>
<p>226 rows × 8 columns</p>
</div>
      <button class="colab-df-convert" onclick="convertToInteractive('df-e8f5977c-fb29-4912-8ee3-8d3b8148a65d')"
              title="Convert this dataframe to an interactive table."
              style="display:none;">

  <svg xmlns="http://www.w3.org/2000/svg" height="24px"viewBox="0 0 24 24"
       width="24px">
    <path d="M0 0h24v24H0V0z" fill="none"/>
    <path d="M18.56 5.44l.94 2.06.94-2.06 2.06-.94-2.06-.94-.94-2.06-.94 2.06-2.06.94zm-11 1L8.5 8.5l.94-2.06 2.06-.94-2.06-.94L8.5 2.5l-.94 2.06-2.06.94zm10 10l.94 2.06.94-2.06 2.06-.94-2.06-.94-.94-2.06-.94 2.06-2.06.94z"/><path d="M17.41 7.96l-1.37-1.37c-.4-.4-.92-.59-1.43-.59-.52 0-1.04.2-1.43.59L10.3 9.45l-7.72 7.72c-.78.78-.78 2.05 0 2.83L4 21.41c.39.39.9.59 1.41.59.51 0 1.02-.2 1.41-.59l7.78-7.78 2.81-2.81c.8-.78.8-2.07 0-2.86zM5.41 20L4 18.59l7.72-7.72 1.47 1.35L5.41 20z"/>
  </svg>
      </button>

  <style>
    .colab-df-container {
      display:flex;
      flex-wrap:wrap;
      gap: 12px;
    }

    .colab-df-convert {
      background-color: #E8F0FE;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: none;
      fill: #1967D2;
      height: 32px;
      padding: 0 0 0 0;
      width: 32px;
    }

    .colab-df-convert:hover {
      background-color: #E2EBFA;
      box-shadow: 0px 1px 2px rgba(60, 64, 67, 0.3), 0px 1px 3px 1px rgba(60, 64, 67, 0.15);
      fill: #174EA6;
    }

    [theme=dark] .colab-df-convert {
      background-color: #3B4455;
      fill: #D2E3FC;
    }

    [theme=dark] .colab-df-convert:hover {
      background-color: #434B5C;
      box-shadow: 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
      filter: drop-shadow(0px 1px 2px rgba(0, 0, 0, 0.3));
      fill: #FFFFFF;
    }
  </style>

      <script>
        const buttonEl =
          document.querySelector('#df-e8f5977c-fb29-4912-8ee3-8d3b8148a65d button.colab-df-convert');
        buttonEl.style.display =
          google.colab.kernel.accessAllowed ? 'block' : 'none';

        async function convertToInteractive(key) {
          const element = document.querySelector('#df-e8f5977c-fb29-4912-8ee3-8d3b8148a65d');
          const dataTable =
            await google.colab.kernel.invokeFunction('convertToInteractive',
                                                     [key], {});
          if (!dataTable) return;

          const docLinkHtml = 'Like what you see? Visit the ' +
            '<a target="_blank" href=https://colab.research.google.com/notebooks/data_table.ipynb>data table notebook</a>'
            + ' to learn more about interactive tables.';
          element.innerHTML = '';
          dataTable['output_type'] = 'display_data';
          await google.colab.output.renderOutput(dataTable, element);
          const docLink = document.createElement('div');
          docLink.innerHTML = docLinkHtml;
          element.appendChild(docLink);
        }
      </script>
    </div>
  </div>




# Visualising our data
It is always good to have a look your data visualised. The former metric provides us with all we need to plot the first two PCA dimensions and add interactive labels.


```python
df['Batch name'] = df['Batch label'].map(str)
fig = px.scatter(df, x="PCA Dimension 1", y="PCA Dimension 2", color="Batch name", 
                 hover_name="Run name", hover_data=["Injection sequence number", "Batch label"])
fig.show()

```


<html>
<head><meta charset="utf-8" /></head>
<body>
    <div>            <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-AMS-MML_SVG"></script><script type="text/javascript">if (window.MathJax) {MathJax.Hub.Config({SVG: {font: "STIX-Web"}});}</script>                <script type="text/javascript">window.PlotlyConfig = {MathJaxConfig: 'local'};</script>
        <script src="https://cdn.plot.ly/plotly-2.8.3.min.js"></script>                <div id="4c3d5c4a-4ab3-40d3-836e-0141c5510234" class="plotly-graph-div" style="height:525px; width:100%;"></div>            <script type="text/javascript">                                    window.PLOTLYENV=window.PLOTLYENV || {};                                    if (document.getElementById("4c3d5c4a-4ab3-40d3-836e-0141c5510234")) {                    Plotly.newPlot(                        "4c3d5c4a-4ab3-40d3-836e-0141c5510234",                        [{"customdata":[[13,4],[14,4],[15,4],[16,4],[17,4],[18,4],[19,4],[20,4],[21,4],[22,4],[5,4],[23,4],[24,4],[25,4],[26,4],[27,4],[28,4],[29,4],[30,4],[31,4],[32,4],[6,4],[33,4],[7,4],[8,4],[9,4],[10,4],[11,4],[12,4]],"hovertemplate":"<b>%{hovertext}</b><br><br>Batch name=4<br>PCA Dimension 1=%{x}<br>PCA Dimension 2=%{y}<br>Injection sequence number=%{customdata[0]}<br>Batch label=%{customdata[1]}<extra></extra>","hovertext":["GCMS ToF sample 10","GCMS ToF sample 11","GCMS ToF sample 12","GCMS ToF sample 13","GCMS ToF sample 14","GCMS ToF sample 15","GCMS ToF sample 16","GCMS ToF sample 17","GCMS ToF sample 18","GCMS ToF sample 19","GCMS ToF sample 2","GCMS ToF sample 20","GCMS ToF sample 21","GCMS ToF sample 22","GCMS ToF sample 23","GCMS ToF sample 24","GCMS ToF sample 25","GCMS ToF sample 26","GCMS ToF sample 27","GCMS ToF sample 28","GCMS ToF sample 29","GCMS ToF sample 3","GCMS ToF sample 30","GCMS ToF sample 4","GCMS ToF sample 5","GCMS ToF sample 6","GCMS ToF sample 7","GCMS ToF sample 8","GCMS ToF sample 9"],"legendgroup":"4","marker":{"color":"#636efa","symbol":"circle"},"mode":"markers","name":"4","orientation":"v","showlegend":true,"x":[-3.3489633839,-0.4470879071,0.2905566121,-0.3069984724,-5.1842079165,7.2263723602,-10.498114593,-1.8478444188,-5.0090218488,-0.7331334459,-3.2004377118,-7.3783032825,1.0397856472,4.9950994081,-3.2913616085,-4.3259115467,-4.037708695,-0.9144311394,-4.6667650928,-4.0681783501,0.6306024972,-4.8651276138,-2.6822831119,-6.1153085456,-11.8407707681,-6.5830897773,-1.1791599605,-1.9468972547,-3.234407891],"xaxis":"x","y":[-2.3414347017,-4.4976917552,-1.9854748977,-1.5333999507,-1.8695850138,-4.6520979386,0.2178688987,-6.9558846923,1.897957498,-4.6845409886,-1.3754645576,0.6046279987,-0.7671619426,-5.8889824839,-4.0840381076,-3.9923664824,-0.2537069808,-0.9517635634,-0.745099422,-3.8174845507,-0.6870928333,-6.9698275224,-4.824004353,-2.7446679861,-2.7620964198,-5.8202052908,1.5141763073,-0.339153104,0.8723962872],"yaxis":"y","type":"scatter"},{"customdata":[[16,7],[17,7],[18,7],[19,7],[20,7],[22,7],[23,7],[24,7],[25,7],[26,7],[27,7],[28,7],[29,7],[30,7],[31,7],[32,7],[33,7],[34,7],[35,7],[36,7],[37,7],[38,7],[39,7],[40,7],[41,7],[42,7],[43,7],[44,7],[45,7],[46,7],[48,7],[49,7],[50,7],[51,7],[52,7],[53,7],[54,7],[55,7],[56,7],[57,7],[58,7],[59,7],[60,7],[61,7],[62,7],[63,7],[64,7],[65,7],[66,7],[67,7],[68,7],[69,7],[70,7],[71,7],[72,7],[76,7],[77,7],[78,7],[79,7],[80,7],[81,7],[82,7],[83,7],[84,7],[85,7],[86,7],[87,7],[88,7],[89,7],[90,7],[91,7],[92,7],[3,7],[4,7],[5,7],[6,7],[7,7],[8,7],[9,7],[10,7],[11,7],[12,7],[13,7],[14,7],[15,7]],"hovertemplate":"<b>%{hovertext}</b><br><br>Batch name=7<br>PCA Dimension 1=%{x}<br>PCA Dimension 2=%{y}<br>Injection sequence number=%{customdata[0]}<br>Batch label=%{customdata[1]}<extra></extra>","hovertext":["GCMS ToF sample 100","GCMS ToF sample 101","GCMS ToF sample 102","GCMS ToF sample 103","GCMS ToF sample 104","GCMS ToF sample 106","GCMS ToF sample 107","GCMS ToF sample 108","GCMS ToF sample 109","GCMS ToF sample 110","GCMS ToF sample 111","GCMS ToF sample 112","GCMS ToF sample 113","GCMS ToF sample 114","GCMS ToF sample 115","GCMS ToF sample 116","GCMS ToF sample 117","GCMS ToF sample 118","GCMS ToF sample 119","GCMS ToF sample 120","GCMS ToF sample 121","GCMS ToF sample 122","GCMS ToF sample 123","GCMS ToF sample 124","GCMS ToF sample 125","GCMS ToF sample 126","GCMS ToF sample 127","GCMS ToF sample 128","GCMS ToF sample 129","GCMS ToF sample 130","GCMS ToF sample 132","GCMS ToF sample 133","GCMS ToF sample 134","GCMS ToF sample 135","GCMS ToF sample 136","GCMS ToF sample 137","GCMS ToF sample 138","GCMS ToF sample 139","GCMS ToF sample 140","GCMS ToF sample 141","GCMS ToF sample 142","GCMS ToF sample 143","GCMS ToF sample 144","GCMS ToF sample 145","GCMS ToF sample 146","GCMS ToF sample 147","GCMS ToF sample 148","GCMS ToF sample 149","GCMS ToF sample 150","GCMS ToF sample 151","GCMS ToF sample 152","GCMS ToF sample 153","GCMS ToF sample 154","GCMS ToF sample 155","GCMS ToF sample 156","GCMS ToF sample 157","GCMS ToF sample 158","GCMS ToF sample 159","GCMS ToF sample 160","GCMS ToF sample 161","GCMS ToF sample 162","GCMS ToF sample 163","GCMS ToF sample 164","GCMS ToF sample 165","GCMS ToF sample 166","GCMS ToF sample 167","GCMS ToF sample 168","GCMS ToF sample 169","GCMS ToF sample 170","GCMS ToF sample 171","GCMS ToF sample 172","GCMS ToF sample 173","GCMS ToF sample 87","GCMS ToF sample 88","GCMS ToF sample 89","GCMS ToF sample 90","GCMS ToF sample 91","GCMS ToF sample 92","GCMS ToF sample 93","GCMS ToF sample 94","GCMS ToF sample 95","GCMS ToF sample 96","GCMS ToF sample 97","GCMS ToF sample 98","GCMS ToF sample 99"],"legendgroup":"7","marker":{"color":"#EF553B","symbol":"circle"},"mode":"markers","name":"7","orientation":"v","showlegend":true,"x":[0.4191257477,6.8241553933,-1.0808863947,-1.707045218,2.8308541748,-2.2338635322,3.9699078343,-2.4770395336,-2.7332267846,-5.1985965443,-1.6871799846,-0.162214613,4.4931694088,1.065013029,-1.1940566219,4.1964218311,-4.9229903804,-0.0487967333,7.9232129003,-2.4167956848,4.188667538,-0.2907648229,-0.9276300068,2.8475911731,-2.968729106,4.1660313629,-1.137933623,1.7420100896,4.759143556,0.3569010485,-4.0831272735,3.5694159259,2.2713740735,-5.0789607892,-0.0752693899,7.1581925537,0.828962944,-1.5693378796,0.3652225255,1.2012539074,0.7432225587,-0.0185043171,-2.9830231055,-1.0151965987,-2.6590623404,1.1782955448,5.3186313176,-10.4677770954,2.3232291491,3.8652035606,6.025908917,1.5578940537,-1.8630675831,2.4299328853,2.4489501744,-8.1272401542,-6.9339250968,-2.6514879488,-8.0560929327,-2.4843500653,-1.5591274019,-4.1491782662,-7.6513289916,-7.7606513161,-4.2396234647,-7.9197018596,-6.0399736461,-3.3695303241,-2.3881146016,-2.2744510576,-0.3913099263,-1.6048077914,-0.1044978744,3.618711788,1.0473173519,5.1268898175,2.7572048852,-1.8963995901,-3.4274871811,-1.7860465161,4.2464436594,2.3680717944,1.6740603069,-2.928425603,10.0001640731],"xaxis":"x","y":[2.0552198422,1.5142354815,2.9945511395,6.0701613531,3.3266278572,3.3685284856,0.5399655333,2.3932072785,2.7643008047,4.0508987872,1.4660293581,0.0770429575,0.0024804836,1.1879740902,0.5707980874,-1.3918382896,1.0451142023,3.5322514915,-2.5080634204,-1.0918833604,-0.5248062282,-0.7546478724,0.8834778808,1.7014956692,2.4943035973,1.6819956954,2.164453404,1.8319649453,0.8101455665,3.1578474235,1.3427308128,-1.9448531516,2.364325228,3.1655048258,-0.2917984184,-8.0143656151,-4.1139242264,2.7958020455,-3.4957487643,-2.7126585146,-6.6259650197,1.4678688788,1.860009365,1.5306572809,2.7205793212,-0.7433254297,-3.3517992711,-0.3683510015,-0.2969785081,-6.1260045659,-2.7918429522,-2.4112026192,0.5809935688,-2.4070162921,-6.2765335862,-3.566985763,1.8899075764,0.7159550768,2.0647094711,-0.1057277641,-3.9440217112,-6.1913732752,-3.5142609684,-2.7538027387,-0.4912709915,-3.004320254,-2.2817738773,-3.6949715311,-3.0744193535,1.7548977324,-5.2636295072,-4.7378502816,2.9918774591,-3.70235352,-1.8028466468,1.6521201628,3.1369325927,3.1258090201,-5.7882477799,2.182551129,1.8413552942,1.0015138509,0.4502112672,4.1755869513,1.9181471533],"yaxis":"y","type":"scatter"},{"customdata":[[4,10],[5,10],[6,10],[7,10],[8,10],[9,10],[10,10],[11,10],[12,10],[13,10],[14,10],[15,10],[16,10],[17,10],[18,10],[19,10],[20,10],[22,10],[23,10],[24,10],[25,10],[26,10],[27,10],[28,10],[29,10],[30,10],[31,10],[32,10],[33,10],[34,10],[35,10],[36,10],[37,10],[38,10],[39,10],[40,10],[41,10],[43,10],[44,10],[45,10],[46,10],[47,10],[48,10],[49,10],[50,10],[51,10],[52,10],[53,10],[54,10],[55,10],[56,10],[57,10],[58,10],[59,10],[60,10],[61,10],[62,10],[63,10],[65,10],[66,10]],"hovertemplate":"<b>%{hovertext}</b><br><br>Batch name=10<br>PCA Dimension 1=%{x}<br>PCA Dimension 2=%{y}<br>Injection sequence number=%{customdata[0]}<br>Batch label=%{customdata[1]}<extra></extra>","hovertext":["GCMS ToF sample 177","GCMS ToF sample 178","GCMS ToF sample 179","GCMS ToF sample 180","GCMS ToF sample 181","GCMS ToF sample 182","GCMS ToF sample 183","GCMS ToF sample 184","GCMS ToF sample 185","GCMS ToF sample 186","GCMS ToF sample 187","GCMS ToF sample 188","GCMS ToF sample 189","GCMS ToF sample 190","GCMS ToF sample 191","GCMS ToF sample 192","GCMS ToF sample 193","GCMS ToF sample 195","GCMS ToF sample 196","GCMS ToF sample 197","GCMS ToF sample 198","GCMS ToF sample 199","GCMS ToF sample 200","GCMS ToF sample 201","GCMS ToF sample 202","GCMS ToF sample 203","GCMS ToF sample 204","GCMS ToF sample 205","GCMS ToF sample 206","GCMS ToF sample 207","GCMS ToF sample 208","GCMS ToF sample 209","GCMS ToF sample 210","GCMS ToF sample 211","GCMS ToF sample 212","GCMS ToF sample 213","GCMS ToF sample 214","GCMS ToF sample 216","GCMS ToF sample 217","GCMS ToF sample 218","GCMS ToF sample 219","GCMS ToF sample 220","GCMS ToF sample 221","GCMS ToF sample 222","GCMS ToF sample 223","GCMS ToF sample 224","GCMS ToF sample 225","GCMS ToF sample 226","GCMS ToF sample 227","GCMS ToF sample 228","GCMS ToF sample 229","GCMS ToF sample 230","GCMS ToF sample 231","GCMS ToF sample 232","GCMS ToF sample 233","GCMS ToF sample 234","GCMS ToF sample 235","GCMS ToF sample 236","GCMS ToF sample 238","GCMS ToF sample 239"],"legendgroup":"10","marker":{"color":"#00cc96","symbol":"circle"},"mode":"markers","name":"10","orientation":"v","showlegend":true,"x":[-0.2399191721,-4.1136913613,-0.6269833457,0.5306315727,-6.592080735,-4.492378256,-1.3028620578,-3.8371703822,-5.2130536703,-5.4317236274,-0.5999563478,2.1531396916,-1.9443562481,0.951283388,2.7826978447,-2.2532581555,-0.0741762409,-7.0497329655,-4.278429051,0.0769809917,7.9025446164,-3.5982310916,-2.3113338329,-1.7110468372,-3.20605726,-3.6158552084,7.520231951,1.4600045217,-3.8326763159,6.1094439358,1.0450705098,-1.1646018992,-0.2774277653,-3.6065836315,-1.776450852,1.7033047566,-1.9458179288,-0.2510462381,-2.4726347321,1.9418319684,-2.0328351118,-0.8091622655,-1.2994065497,-1.5601348705,-4.1472603067,0.9442454758,-3.5628871304,-4.6960341411,0.7348968302,-3.3741246267,1.9625296323,3.9293009716,-1.205756014,2.8494074208,3.7449335931,-1.3034700542,1.8941360122,0.2289366469,-0.3611115399,-2.2606294339],"xaxis":"x","y":[1.8387353375,1.0740775321,0.1835648149,0.679158744,-0.3750873679,1.9841123762,0.6193101644,0.660805318,3.4699798867,0.5116066126,2.190893902,-0.555333107,-0.2790107249,1.8409696954,0.530709381,-2.1822527379,1.7141617973,-0.0011017748,2.3063334903,-0.188886904,-5.3206715922,4.4367196141,0.138546764,2.4113359288,-0.4279627921,0.1660507663,-2.6017667638,1.8171734659,-1.9287317332,-0.4871874161,0.0066686902,-2.8455727834,0.8987028496,0.6110709048,2.7598142193,-4.6815935268,0.9227273089,-4.4617670261,3.304331427,-4.9056616075,0.8563141357,-2.998209467,1.7242970052,-1.2480321852,-0.975974124,1.8048862439,1.4810275414,-0.4489186938,-7.8716066565,1.8305754809,2.3758996966,0.511994141,2.3561564188,-1.8099415196,-6.9678750052,2.2163383495,-4.3832101315,-0.0977442974,0.4469612911,0.6190589068],"yaxis":"y","type":"scatter"},{"customdata":[[2,5],[3,5],[4,5],[5,5],[6,5],[7,5],[8,5],[9,5],[10,5],[11,5],[12,5],[13,5],[14,5],[15,5],[16,5],[17,5],[18,5],[19,5],[20,5],[21,5],[22,5],[23,5],[24,5],[25,5],[26,5],[27,5],[28,5],[29,5],[30,5],[31,5],[32,5],[33,5],[34,5],[35,5],[36,5],[38,5],[39,5],[40,5],[41,5],[42,5],[43,5],[44,5],[45,5],[46,5],[47,5],[48,5],[49,5],[50,5],[51,5],[52,5],[53,5],[54,5]],"hovertemplate":"<b>%{hovertext}</b><br><br>Batch name=5<br>PCA Dimension 1=%{x}<br>PCA Dimension 2=%{y}<br>Injection sequence number=%{customdata[0]}<br>Batch label=%{customdata[1]}<extra></extra>","hovertext":["GCMS ToF sample 32","GCMS ToF sample 33","GCMS ToF sample 34","GCMS ToF sample 35","GCMS ToF sample 36","GCMS ToF sample 37","GCMS ToF sample 38","GCMS ToF sample 39","GCMS ToF sample 40","GCMS ToF sample 41","GCMS ToF sample 42","GCMS ToF sample 43","GCMS ToF sample 44","GCMS ToF sample 45","GCMS ToF sample 46","GCMS ToF sample 47","GCMS ToF sample 48","GCMS ToF sample 49","GCMS ToF sample 50","GCMS ToF sample 51","GCMS ToF sample 52","GCMS ToF sample 53","GCMS ToF sample 54","GCMS ToF sample 55","GCMS ToF sample 56","GCMS ToF sample 57","GCMS ToF sample 58","GCMS ToF sample 59","GCMS ToF sample 60","GCMS ToF sample 61","GCMS ToF sample 62","GCMS ToF sample 63","GCMS ToF sample 64","GCMS ToF sample 65","GCMS ToF sample 66","GCMS ToF sample 68","GCMS ToF sample 69","GCMS ToF sample 70","GCMS ToF sample 71","GCMS ToF sample 72","GCMS ToF sample 73","GCMS ToF sample 74","GCMS ToF sample 75","GCMS ToF sample 76","GCMS ToF sample 77","GCMS ToF sample 78","GCMS ToF sample 79","GCMS ToF sample 80","GCMS ToF sample 81","GCMS ToF sample 82","GCMS ToF sample 83","GCMS ToF sample 84"],"legendgroup":"5","marker":{"color":"#ab63fa","symbol":"circle"},"mode":"markers","name":"5","orientation":"v","showlegend":true,"x":[3.5012376744,4.7247233268,2.4099708448,0.2868303919,0.6393485354,-0.5288303333,-0.9719860724,3.0923171347,7.2981571438,1.1822851458,1.3488446334,2.231647972,2.7491393016,12.0457639249,6.282702297,1.7760115076,2.1585026031,1.8310786124,3.8160350734,4.2813855441,9.1643828848,4.1860017961,6.5689740649,12.3831848323,7.481412766,1.3363157101,3.4447531681,3.849074158,4.6122127984,3.7304911054,0.1042706374,4.2398502663,4.9181056021,0.5174171321,7.5574701484,6.8105359833,4.1691413147,6.0136378152,2.0571260202,1.7062619383,3.5873517455,1.2681832303,3.0395313236,0.4216375015,2.4870567016,0.9305310838,2.0223972375,-0.7278680161,-3.4396024067,-1.3879392689,1.8532049653,-0.7323080554],"xaxis":"x","y":[3.1139341738,-0.4880301904,1.3030136002,2.8688932063,2.1926134768,2.6298741845,3.025650846,1.2350628205,0.1336670141,3.1024683047,4.9055041462,3.1173516042,1.5730926887,-0.5070724258,3.4016550643,4.0467956149,6.093295473,5.0591633712,2.5247364196,2.647086586,1.6895717109,2.5580686197,0.6806439599,-2.9500776533,2.41717624,5.0418393595,4.5406613701,5.5848945381,1.4384628468,2.4950964741,1.1487093353,3.1176371508,0.2318095042,4.2757365759,0.2310854792,0.9173859454,-0.2008158459,-6.3773907519,-4.2728006741,-2.0448990134,-3.88337042,0.3256674661,3.5027264787,-0.5171001085,1.9175499599,4.6431566297,-5.1688101823,1.4524116058,3.679482305,1.8253918947,3.0501141436,4.596802953],"yaxis":"y","type":"scatter"}],                        {"template":{"data":{"bar":[{"error_x":{"color":"#2a3f5f"},"error_y":{"color":"#2a3f5f"},"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"bar"}],"barpolar":[{"marker":{"line":{"color":"#E5ECF6","width":0.5},"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"barpolar"}],"carpet":[{"aaxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"baxis":{"endlinecolor":"#2a3f5f","gridcolor":"white","linecolor":"white","minorgridcolor":"white","startlinecolor":"#2a3f5f"},"type":"carpet"}],"choropleth":[{"colorbar":{"outlinewidth":0,"ticks":""},"type":"choropleth"}],"contour":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"contour"}],"contourcarpet":[{"colorbar":{"outlinewidth":0,"ticks":""},"type":"contourcarpet"}],"heatmap":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"heatmap"}],"heatmapgl":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"heatmapgl"}],"histogram":[{"marker":{"pattern":{"fillmode":"overlay","size":10,"solidity":0.2}},"type":"histogram"}],"histogram2d":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"histogram2d"}],"histogram2dcontour":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"histogram2dcontour"}],"mesh3d":[{"colorbar":{"outlinewidth":0,"ticks":""},"type":"mesh3d"}],"parcoords":[{"line":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"parcoords"}],"pie":[{"automargin":true,"type":"pie"}],"scatter":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scatter"}],"scatter3d":[{"line":{"colorbar":{"outlinewidth":0,"ticks":""}},"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scatter3d"}],"scattercarpet":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scattercarpet"}],"scattergeo":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scattergeo"}],"scattergl":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scattergl"}],"scattermapbox":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scattermapbox"}],"scatterpolar":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scatterpolar"}],"scatterpolargl":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scatterpolargl"}],"scatterternary":[{"marker":{"colorbar":{"outlinewidth":0,"ticks":""}},"type":"scatterternary"}],"surface":[{"colorbar":{"outlinewidth":0,"ticks":""},"colorscale":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"type":"surface"}],"table":[{"cells":{"fill":{"color":"#EBF0F8"},"line":{"color":"white"}},"header":{"fill":{"color":"#C8D4E3"},"line":{"color":"white"}},"type":"table"}]},"layout":{"annotationdefaults":{"arrowcolor":"#2a3f5f","arrowhead":0,"arrowwidth":1},"autotypenumbers":"strict","coloraxis":{"colorbar":{"outlinewidth":0,"ticks":""}},"colorscale":{"diverging":[[0,"#8e0152"],[0.1,"#c51b7d"],[0.2,"#de77ae"],[0.3,"#f1b6da"],[0.4,"#fde0ef"],[0.5,"#f7f7f7"],[0.6,"#e6f5d0"],[0.7,"#b8e186"],[0.8,"#7fbc41"],[0.9,"#4d9221"],[1,"#276419"]],"sequential":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]],"sequentialminus":[[0.0,"#0d0887"],[0.1111111111111111,"#46039f"],[0.2222222222222222,"#7201a8"],[0.3333333333333333,"#9c179e"],[0.4444444444444444,"#bd3786"],[0.5555555555555556,"#d8576b"],[0.6666666666666666,"#ed7953"],[0.7777777777777778,"#fb9f3a"],[0.8888888888888888,"#fdca26"],[1.0,"#f0f921"]]},"colorway":["#636efa","#EF553B","#00cc96","#ab63fa","#FFA15A","#19d3f3","#FF6692","#B6E880","#FF97FF","#FECB52"],"font":{"color":"#2a3f5f"},"geo":{"bgcolor":"white","lakecolor":"white","landcolor":"#E5ECF6","showlakes":true,"showland":true,"subunitcolor":"white"},"hoverlabel":{"align":"left"},"hovermode":"closest","mapbox":{"style":"light"},"paper_bgcolor":"white","plot_bgcolor":"#E5ECF6","polar":{"angularaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"bgcolor":"#E5ECF6","radialaxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"scene":{"xaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","gridwidth":2,"linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white"},"yaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","gridwidth":2,"linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white"},"zaxis":{"backgroundcolor":"#E5ECF6","gridcolor":"white","gridwidth":2,"linecolor":"white","showbackground":true,"ticks":"","zerolinecolor":"white"}},"shapedefaults":{"line":{"color":"#2a3f5f"}},"ternary":{"aaxis":{"gridcolor":"white","linecolor":"white","ticks":""},"baxis":{"gridcolor":"white","linecolor":"white","ticks":""},"bgcolor":"#E5ECF6","caxis":{"gridcolor":"white","linecolor":"white","ticks":""}},"title":{"x":0.05},"xaxis":{"automargin":true,"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","zerolinewidth":2},"yaxis":{"automargin":true,"gridcolor":"white","linecolor":"white","ticks":"","title":{"standoff":15},"zerolinecolor":"white","zerolinewidth":2}}},"xaxis":{"anchor":"y","domain":[0.0,1.0],"title":{"text":"PCA Dimension 1"}},"yaxis":{"anchor":"x","domain":[0.0,1.0],"title":{"text":"PCA Dimension 2"}},"legend":{"title":{"text":"Batch name"},"tracegroupgap":0},"margin":{"t":60}},                        {"responsive": true}                    ).then(function(){

var gd = document.getElementById('4c3d5c4a-4ab3-40d3-836e-0141c5510234');
var x = new MutationObserver(function (mutations, observer) {{
        var display = window.getComputedStyle(gd).display;
        if (!display || display === 'none') {{
            console.log([gd, 'removed!']);
            Plotly.purge(gd);
            observer.disconnect();
        }}
}});

// Listen for the removal of the full notebook cells
var notebookContainer = gd.closest('#notebook-container');
if (notebookContainer) {{
    x.observe(notebookContainer, {childList: true});
}}

// Listen for the clearing of the current output cell
var outputEl = gd.closest('.output');
if (outputEl) {{
    x.observe(outputEl, {childList: true});
}}

                        })                };                            </script>        </div>
</body>
</html>

