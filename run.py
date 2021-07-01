import requests
import json
import pprint
import pandas as pd
import numpy as np
import xmltodict
from xml.etree import ElementTree
from pymed import PubMed
from Bio import Entrez
import plotly
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# https://stackoverflow.com/questions/57053378/query-pubmed-with-python-how-to-get-all-article-details-from-query-to-pandas-d
pubmed = PubMed(tool="PubMedSearcher", email="martina.fonseca@nhsx.nhs.uk")
results = pubmed.query(
    "nhsx[affiliation]", max_results=500
)  # number might need to be updated in future, for now low
articleList = []
articleInfo = []

for article in results:
    # Print the type of object we've found (can be either PubMedBookArticle or PubMedArticle).
    articleDict = article.toDict()  # convert to dictionary
    articleList.append(articleDict)

# Generate list of dict records which will hold all article details that could be fetch from PUBMED API
for article in articleList:
    # Sometimes article['pubmed_id'] contains list separated with comma - take first pubmedId in that list - thats article pubmedId
    pubmedId = article["pubmed_id"].partition("\n")[0]  # keep only pubmed id
    # Append article info to dictionary #
    articleInfo.append(
        {
            u"pubmed_id": pubmedId,
            u"title": article["title"],
            u"keywords": article["keywords"],
            u"journal": article["journal"],
            u"abstract": article["abstract"],
            u"conclusions": article["conclusions"],
            u"methods": article["methods"],
            u"results": article["results"],
            u"copyrights": article["copyrights"],
            u"doi": article["doi"],
            u"publication_date": article["publication_date"],
            u"authors": article["authors"],
        }
    )

# Convert list of dictionaries to pandas DataFrame
articlesPD = pd.DataFrame.from_dict(articleInfo)

# Unravel author list, retain initial + surname
i = 0
Authors_np = np.array([])
for element in articlesPD["authors"]:
    mystring = ""
    for author in element:
        if author["affiliation"].lower().find("nhsx") == -1:
            mystring = mystring + author["lastname"] + " " + author["initials"] + ", "
        else:
            mystring = (
                mystring
                + "<b>"
                + author["lastname"]
                + " "
                + author["initials"]
                + "</b>, "
            )

    Authors_np = np.append(Authors_np, mystring[:-2])
    i = i + 1
articlesPD["Authors"] = Authors_np

# Obtain number of forward cites (only from Pubmed articles cited in PMC - current API that is available)

# https://gist.github.com/mcfrank/c1ec74df1427278cbe53
Entrez.email = "martina.fonseca@nhsx.nhs.uk"


def get_onwardlinks_id(pmid):
    link_list = []
    links = Entrez.elink(dbfrom="pubmed", id=pmid, linkname="pubmed_pmc_refs")
    record = Entrez.read(links)
    if record[0]["LinkSetDb"] != []:
        records = record[0][u"LinkSetDb"][0][u"Link"]
        for link in records:
            link_list.append(link[u"Id"])
    return link_list


# https://stackoverflow.com/questions/26483254/python-pandas-insert-list-into-a-cell
i = 0
articlesPD["citations_list"] = np.nan
articlesPD["citations_list"] = articlesPD["citations_list"].astype(object)
for element in articlesPD["pubmed_id"]:
    citations_this = get_onwardlinks_id(element)
    articlesPD.at[i, "citations_list"] = citations_this
    i = i + 1
articlesPD["No. PMC Citations"] = articlesPD["citations_list"].apply(lambda x: len(x))

# create DOI column that is html link to DOI page
articlesPD["DOI"] = (
    "<a href='"
    + "http://doi.org/"
    + articlesPD["doi"]
    + "'>"
    + articlesPD["doi"]
    + "</a>"
)
", ".join([str(x) for x in articlesPD["keywords"][2]])  # list comprehension

# article Key words
articlesPD["Keywords"] = articlesPD["keywords"].apply(
    lambda keyword_list: ", ".join([str(x) for x in keyword_list])
)

# create DOI column that is html link to DOI page
articlesPD["DOIbullets"] = (
    "<a href='"
    + "http://doi.org/"
    + articlesPD["doi"]
    + "'>"
    + articlesPD["title"]
    + "</a>"
)

# cs branch - adapted
def ulify(elements):
    string = "<ul>"
    string += "".join(["<li>" + str(s) + "</li>" for s in elements])
    string += "</ul>"
    return string


html_list = ulify(articlesPD["DOIbullets"])

with open("_includes/publications.html", "w") as file:
    file.write(html_list)

# subset for table
articlesPD_sel = articlesPD[
    [
        "publication_date",
        "DOIbullets",
        "journal",
        "Authors",
        "No. PMC Citations",
        "Keywords",
    ]
].copy()
articlesPD_sel = articlesPD_sel.rename(
    columns={
        "DOIbullets": "Publication Title",
        "journal": "Journal",
        "publication_date": "Publication Date",
    }
)

# new NHS.UK style table
aggregate_latest_html = articlesPD_sel.to_html(
    index=False, render_links=True, escape=False
)
aggregate_latest_html = aggregate_latest_html.replace(
    "dataframe", "nhsuk-table__panel-with-heading-tab"
)
aggregate_latest_html = aggregate_latest_html.replace('border="1"', "")
with open("_includes/NHSUK_table.html", "w") as file:
    file.write(aggregate_latest_html)

# Grab timestamp
data_updated = datetime.now().strftime("%d/%m/%Y")

# Write out to file (.html)
html_str = (
    '<p><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" width="16" height="16"><path fill-rule="evenodd" d="M1.5 8a6.5 6.5 0 1113 0 6.5 6.5 0 01-13 0zM8 0a8 8 0 100 16A8 8 0 008 0zm.5 4.75a.75.75 0 00-1.5 0v3.5a.75.75 0 00.471.696l2.5 1a.75.75 0 00.557-1.392L8.5 7.742V4.75z"></path></svg> Latest Data: '
    + data_updated
    + "</p>"
)
with open("_includes/update.html", "w") as file:
    file.write(html_str)

# Fetching also yearly publications with NHS[affiliation] authors (time-series)


def get_links_term(term, retmax=10000):
    links = Entrez.esearch(db="pubmed", retmax=retmax, term=term)
    record = Entrez.read(links)
    # link_list = record[u'IdList']

    return record


df_nhs_y = pd.DataFrame({"year": np.arange(2010, 2022)})
df_nhs_y.set_index("year", inplace=True)  # reset index
df_nhs_y["publications_count"] = np.nan  # initialise

for i in df_nhs_y.index:
    search_string = (
        '(nhs[Affiliation]) AND (("'
        + str(i)
        + '/01/01"[Date - Publication] : "'
        + str(i)
        + '/12/31"[Date - Publication]))'
    )
    df_nhs_y.loc[i]["publications_count"] = get_links_term(
        search_string, retmax=10000000
    )["Count"]
df_nhs_y.index
df_nhs_y["Year_datetime"] = pd.to_datetime(df_nhs_y.index, format="%Y")

# Plotly figure
fig = go.Figure([go.Bar(x=df_nhs_y.index, y=df_nhs_y["publications_count"])])

# Asthetics of the plot
fig.update_layout(
    {"plot_bgcolor": "rgba(0, 0, 0, 0)", "paper_bgcolor": "rgba(0, 0, 0, 0)"},
    autosize=True,
    margin=dict(l=50, r=50, b=50, t=50, pad=4, autoexpand=True),
    # height=1000,
    # hovermode="x",
)

# Add title and dynamic range selector to x axis
fig.update_xaxes(
    title_text="Date",
    rangeselector=dict(
        buttons=list(
            [
                # dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="5y", step="year", stepmode="backward"),
                dict(step="all"),
            ]
        )
    ),
)

# Add title to y axis
fig.update_yaxes(title_text="Count of publications")

# Write out to file (.html)
config = {"displayModeBar": False, "displaylogo": False}
plotly_obj = plotly.offline.plot(
    fig, include_plotlyjs=False, output_type="div", config=config
)
with open("_includes/plotly_obj.html", "w") as file:
    file.write(plotly_obj)