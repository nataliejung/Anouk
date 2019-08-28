import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import xlsxwriter
import util
from tika import parser
from pprint import pprint




def heapMap(uploadedFile):
    
    parsedPDF = parser.from_file(uploadedFile, xmlContent=True)
   
    parsedPDF.keys()

    rawContent = parsedPDF["content"]
    allPages = []
    startMarker = "<div class=\"page\">"
    endMarker = "</div>"

    smLength = len(startMarker)

    # cursor starts at zero
    cursor = 0

    while 1:

        cursor = rawContent.find(startMarker, cursor+smLength)
        if cursor == -1:
            break
        pageEnd = rawContent.find(endMarker, cursor)

        allPages.append(rawContent[cursor+smLength:pageEnd])

    # Remove xml markers
    for idx in range(len(allPages)):
        allPages[idx] = re.sub("<[^<]+>", "", allPages[idx])


    def removeAll(removable, target): return [target.remove(
        removable) for _ in range(target.count(removable))]


    def getPage_(pagenr):
        """Helper function to return a single
        page from the raw document"""
        res = allPages[pagenr-1].split("\n")

        # remove empty lines
        removeAll("", res)
        removeAll(" ", res)

        # remove full stops if they are
        # preceded and succeeded by a digit
        for idx, line in enumerate(res):
            res[idx] = re.sub("(?:(?<=\d)(?=.\d))\.", "", res[idx])

        return res


    def getPage(pagenrs):
        """Returns a list of lines from the page
        pagenrs. pagenrs can also be a list of numbers,
        in which case this function returns a list of
        the target allPages.

        Removes empty lines
        """

        if isinstance(pagenrs, list):
            res = []
            for pagenr in pagenrs:
                res.extend(getPage_(pagenr))

        elif isinstance(pagenrs, int):
            res = getPage_(pagenrs)

        else:
            raise Exception("Not a page number(s)!")

        return res


    targetFields = ["Name", "Notes", "EUR-2018", "USD-2018", "TL-2018", "TL-2017"]


    def maybeNumeric(string):
        try:
            return int(string)
        except ValueError:
            return string


    def pageToDf(page, minNumeric, missing="-"):
        """The page variable is a list of non-empty
        lines that the page contains, to be used with
        the getPage function.
        """

        res = []

        for line in page:
            line = line.split(" ")

            # Remove empties
            removeAll("", line)

            ssRes = []
            nsRes = []

            for substring in line:
                # Remove parentheses around numbers
                if substring[0] == "(" and substring[-1] == ")":
                    substring = substring[1:-1]
                # Check if the substring is a number
                # and put in the corresponding list
                undecided = maybeNumeric(substring)

                if isinstance(undecided, int):
                    # Is a number
                    nsRes.append(undecided)
                elif undecided == missing:
                    # The value is missing in the table
                    # But it should still be numeric
                    nsRes.append(None)
                else:
                    # Is the name of the data row
                    ssRes.append(undecided)

            if len(nsRes) >= minNumeric:
                # Candidate for data
                # Remove anything before Notes field
                nsRes = nsRes[-(minNumeric+1):]
                name = " ".join(ssRes)
                nsRes.insert(0, name)
                res.append(nsRes)
            else:
                continue

        # add None for missing notes
        for idx, line in enumerate(res):
            if len(line) == minNumeric+1:
                line.insert(1, None)
                res[idx] = line

        #Only for the first row for YEAR value        
        if str(res[0][0]) == '' and str(res[0][1]) == "None":
            del (res[0])
            
        return pd.DataFrame.from_records(res, columns=targetFields)

    # Add 1-year changes


    def addChanges(fdf):
        fdf["TL-Diff"] = fdf["TL-2018"] - fdf["TL-2017"]
        fdf["% Change"] = round((fdf["TL-Diff"] / fdf["TL-2017"]) * 100,1)



    # Green if change is less than or equal to 5%
    # Amber if change is between 5-10%
    # Red if change is larger than 10%

    def colorcode(row):
        res = ["" for _ in row.index]
        pdiff = np.abs(row["% Change"])
        if pdiff <= 5: #Green
            res[row.index.get_loc("TL-Diff")] = "background-color: #92d050"
            res[row.index.get_loc("% Change")] = "background-color: #92d050"
        elif pdiff <= 10: #Light Yello
            res[row.index.get_loc("TL-Diff")] = "background-color: #ffc031"
            res[row.index.get_loc("% Change")] = "background-color: #ffc031"
        else:  #Red
            res[row.index.get_loc("TL-Diff")] = "background-color: #FF0000"
            res[row.index.get_loc("% Change")] = "background-color: #FF0000"
        return res


    numFields = 4
    CBS = pageToDf(getPage([156, 157]), numFields)
    CIS = pageToDf(getPage(158), numFields)
    CCF = pageToDf(getPage(162), numFields)

    # Add changes 2017-2018
    addChanges(CBS)
    addChanges(CIS)
    addChanges(CCF)
    
    #Delete any file
    util.clean_file(util.file_decoder(uploadedFile))

    # Export to excel
    with pd.ExcelWriter(util.file_decoder(uploadedFile)) as writer:
        CBS.style.apply(colorcode, axis=1).to_excel(writer, sheet_name="CBS")
        CIS.style.apply(colorcode, axis=1).to_excel(writer, sheet_name="CIS")
        CCF.style.apply(colorcode, axis=1).to_excel(writer, sheet_name="CCF")
        util.file_width(CBS, writer, "CBS")           
        util.file_width(CIS, writer, "CIS")     
        util.file_width(CCF, writer, "CCF")
    

    

        

    
       
    
      

    # Parameters for plotting
    plotKwargs = {
        "x": "Name",
        "figsize": (17, 12),
        "kind": "bar",
        "fontsize": 20,
    }


    def plotChanges(fdf):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax1 = ax.twinx()

        def align_yaxis(ax1, v1, ax2, v2):
            """adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
            _, y1 = ax1.transData.transform((0, v1))
            _, y2 = ax2.transData.transform((0, v2))
            inv = ax2.transData.inverted()
            _, dy = inv.transform((0, 0)) - inv.transform((0, y1-y2))
            miny, maxy = ax2.get_ylim()
            ax2.set_ylim(miny+dy, maxy+dy)

        fdf.plot(y="% Change", ax=ax, **plotKwargs, position=0, color="red")
        fdf.plot(y="TL-Diff", ax=ax1, **plotKwargs, position=1, color="blue")

        align_yaxis(ax, 0, ax1, 0)


  #  plotChanges(CBS)

  #  plotChanges(CIS)

  #  plotChanges(CCF)




#heapMap("Koc-Holding-2018-Annual-Report.pdf")