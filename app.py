from quickchart import QuickChart


import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_upstage import UpstageLayoutAnalysisLoader
from langchain_upstage import ChatUpstage

import os
import json
import tempfile



solarllm = ChatUpstage()

qc = QuickChart()
qc.width = 500
qc.height = 300


chart_examples = """
{
  type: 'bar',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      { label: 'Dogs', data: [50, 60, 70, 180, 190] },
      { label: 'Cats', data: [100, 200, 300, 400, 500] },
    ],
  },
}
---
{
  type: 'line',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      {
        label: 'Dogs',
        data: [50, 60, 70, 180, 190],
        fill: false,
        borderColor: 'blue',
      },
      {
        label: 'Cats',
        data: [100, 200, 300, 400, 500],
        fill: false,
        borderColor: 'green',
      },
    ],
  },
}
---

{
  type: 'radar',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      { label: 'Dogs', data: [50, 60, 70, 180, 190] },
      { label: 'Cats', data: [100, 200, 300, 400, 500] },
    ],
  },
}

---
{
  type: 'pie',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [{ data: [50, 60, 70, 180, 190] }],
  },
}

---

{
  type: 'doughnut',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [{ data: [50, 60, 70, 180, 190] }],
  },
  options: {
    plugins: {
      doughnutlabel: {
        labels: [{ text: '550', font: { size: 20 } }, { text: 'total' }],
      },
    },
  },
}

---
{
  type: 'polarArea',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [{ data: [50, 60, 70, 180, 190] }],
  },
}

---

{
  type: 'scatter',
  data: {
    datasets: [
      {
        label: 'Data 1',
        data: [
          { x: 2, y: 4 },
          { x: 3, y: 3 },
          { x: -10, y: 0 },
          { x: 0, y: 10 },
          { x: 10, y: 5 },
        ],
      },
    ],
  },
}

---

{
  type: 'bubble',
  data: {
    datasets: [
      {
        label: 'Data 1',
        data: [
          { x: 1, y: 4, r: 9 },
          { x: 2, y: 4, r: 6 },
          { x: 3, y: 8, r: 30 },
          { x: 0, y: 10, r: 1 },
          { x: 10, y: 5, r: 5 },
        ],
      },
    ],
  },
}

---

{
  type: 'radialGauge',
  data: { datasets: [{ data: [70], backgroundColor: 'green' }] },
}

---

{
  type: 'gauge',
  data: {
    datasets: [
      {
        value: 50,
        data: [20, 40, 60],
        backgroundColor: ['green', 'orange', 'red'],
        borderWidth: 2,
      },
    ],
  },
  options: {
    valueLabel: {
      fontSize: 22,
      backgroundColor: 'transparent',
      color: '#000',
      formatter: function (value, context) {
        return value + ' mph';
      },
      bottomMarginPercentage: 10,
    },
  },
}

---

{
  type: 'violin',
  data: {
    labels: [2012, 2013, 2014, 2015],
    datasets: [
      {
        label: 'Data',
        data: [
          [12, 6, 3, 4],
          [1, 8, 8, 15],
          [1, 1, 1, 2, 3, 5, 9, 8],
          [19, -3, 18, 8, 5, 9, 9],
        ],
        backgroundColor: 'rgba(56,123,45,0.2)',
        borderColor: 'rgba(56,123,45,1.9)',
      },
    ],
  },
}
---

{
  type: 'sparkline',
  data: { datasets: [{ data: [140, 60, 274, 370, 199] }] },
}

---

{
  type: 'sankey',
  data: {
    datasets: [
      {
        data: [
          { from: 'Step A', to: 'Step B', flow: 10 },
          { from: 'Step A', to: 'Step C', flow: 5 },
          { from: 'Step B', to: 'Step C', flow: 10 },
          { from: 'Step D', to: 'Step C', flow: 7 },
        ]
      },
    ],
  },
}

---

{
  type: 'progressBar',
  data: {
    datasets: [
      {
        data: [50],
      },
    ],
  },
}

---

{
  type: 'bar',
  data: {
    labels: ['January', 'February', 'March', 'April', 'May'],
    datasets: [
      { label: 'Dogs', data: [50, 60, 70, 180, 190] },
      { label: 'Cats', data: [100, 200, 300, 400, 500] },
      {
        type: 'line',
        fill: false,
        label: 'Potatoes',
        data: [100, 400, 200, 400, 700],
      },
    ],
  },
}

"""



def get_gc_config(text_description: str, chart_examples: str = chart_examples):

    prompt = ChatPromptTemplate.from_template(
        """You are a chart generate  expert. We are using https://quickchart.io/ to generate the chart.
For this, tou need to generate json like chart configuration. 
Please see several examples of chart configurations and generate a new chart configuration based text description.
Please select the best chart type and provide corract chat configuration.
Please do not include the text description. Only include the chart configuration in json format.
---
CHART EXAMPLES:
{chart_examples}
---
Text Description:
{text_description}
"""
    )

    chain = prompt | solarllm | StrOutputParser()
    response = chain.invoke({"text_description": text_description, "chart_examples": chart_examples})
    return response


def get_html_from_image(image):
    content = ""
    if uploaded_file and uploaded_file.name:
        with st.status("Processing the data ..."):
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, uploaded_file.name)
                print(file_path)

                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                layzer = UpstageLayoutAnalysisLoader(
                    file_path, use_ocr=True
                )
                # For improved memory efficiency, consider using the lazy_load method to load documents page by page.
                docs = layzer.load()  # or layzer.lazy_load()
                st.write(f"Loaded {len(docs)} pages from {uploaded_file.name}")

                for doc in docs:
                    st.write(doc)
                    content += "\n\n" + str(doc)

    return content

if __name__ == "__main__":
    chart_explanation = """Please show me a chart of the number of dogs and cats in January, February, March, April, and May.
    dogs: 50, 60, 70, 180, 190
    cats: 100, 200, 300, 400, 500
Use more colors and show me something creative."""
    st.set_page_config(
        page_title="Solar Chart",
        page_icon="📊",
        layout="wide",
    )
    st.title("🌞 Solar Chart 📊")
    st.write("Please provide the chart explanation and I will generate the chart")

    chart_explanation = st.text_area("Write your chart explanation here", chart_explanation, height=120)

    uploaded_file = st.file_uploader(
        "Otional: Choose image that includes numbers or table", type=["png", "jpeg", "jpg"]
    )

    if st.button("Show me the chart"):
        if uploaded_file and uploaded_file.name:
            chart_explanation += "\n\n" + get_html_from_image(uploaded_file)
        
        with st.status("Generating the chart configuration ..."):
            for i in range(3):
                try:
                    json = get_gc_config(chart_explanation)
                    st.json(json)
                    break
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.warning("Please try again!")
        
        with st.status("Generating the chart ...", expanded=True):
            qc.config = json
            # You can get the chart URL...
            print(qc.get_url())

            # Get the image as a variable...
            #image = qc.get_image()

            # ...and display it
            #st.image(image, caption="Generated Chart")
            st.image(qc.get_url(), caption="Generated Chart")

