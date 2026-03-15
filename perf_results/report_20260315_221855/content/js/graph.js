/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
$(document).ready(function() {

    $(".click-title").mouseenter( function(    e){
        e.preventDefault();
        this.style.cursor="pointer";
    });
    $(".click-title").mousedown( function(event){
        event.preventDefault();
    });

    // Ugly code while this script is shared among several pages
    try{
        refreshHitsPerSecond(true);
    } catch(e){}
    try{
        refreshResponseTimeOverTime(true);
    } catch(e){}
    try{
        refreshResponseTimePercentiles();
    } catch(e){}
});


var responseTimePercentilesInfos = {
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 5280.0, "series": [{"data": [[0.0, 1.0], [0.1, 3.0], [0.2, 6.0], [0.3, 8.0], [0.4, 10.0], [0.5, 13.0], [0.6, 20.0], [0.7, 26.0], [0.8, 32.0], [0.9, 34.0], [1.0, 35.0], [1.1, 37.0], [1.2, 39.0], [1.3, 41.0], [1.4, 41.0], [1.5, 43.0], [1.6, 44.0], [1.7, 45.0], [1.8, 46.0], [1.9, 46.0], [2.0, 47.0], [2.1, 48.0], [2.2, 48.0], [2.3, 49.0], [2.4, 49.0], [2.5, 49.0], [2.6, 50.0], [2.7, 50.0], [2.8, 51.0], [2.9, 51.0], [3.0, 52.0], [3.1, 52.0], [3.2, 53.0], [3.3, 53.0], [3.4, 54.0], [3.5, 54.0], [3.6, 55.0], [3.7, 56.0], [3.8, 56.0], [3.9, 57.0], [4.0, 57.0], [4.1, 57.0], [4.2, 58.0], [4.3, 58.0], [4.4, 59.0], [4.5, 59.0], [4.6, 60.0], [4.7, 60.0], [4.8, 60.0], [4.9, 61.0], [5.0, 61.0], [5.1, 62.0], [5.2, 62.0], [5.3, 62.0], [5.4, 63.0], [5.5, 63.0], [5.6, 63.0], [5.7, 64.0], [5.8, 64.0], [5.9, 64.0], [6.0, 64.0], [6.1, 64.0], [6.2, 65.0], [6.3, 65.0], [6.4, 65.0], [6.5, 65.0], [6.6, 66.0], [6.7, 66.0], [6.8, 66.0], [6.9, 66.0], [7.0, 67.0], [7.1, 67.0], [7.2, 67.0], [7.3, 67.0], [7.4, 68.0], [7.5, 68.0], [7.6, 68.0], [7.7, 68.0], [7.8, 69.0], [7.9, 69.0], [8.0, 69.0], [8.1, 69.0], [8.2, 69.0], [8.3, 70.0], [8.4, 70.0], [8.5, 70.0], [8.6, 70.0], [8.7, 71.0], [8.8, 71.0], [8.9, 71.0], [9.0, 71.0], [9.1, 71.0], [9.2, 72.0], [9.3, 72.0], [9.4, 72.0], [9.5, 72.0], [9.6, 73.0], [9.7, 73.0], [9.8, 73.0], [9.9, 73.0], [10.0, 74.0], [10.1, 74.0], [10.2, 74.0], [10.3, 74.0], [10.4, 75.0], [10.5, 75.0], [10.6, 75.0], [10.7, 75.0], [10.8, 75.0], [10.9, 76.0], [11.0, 76.0], [11.1, 76.0], [11.2, 76.0], [11.3, 77.0], [11.4, 77.0], [11.5, 77.0], [11.6, 77.0], [11.7, 78.0], [11.8, 78.0], [11.9, 78.0], [12.0, 78.0], [12.1, 78.0], [12.2, 79.0], [12.3, 79.0], [12.4, 79.0], [12.5, 79.0], [12.6, 79.0], [12.7, 79.0], [12.8, 80.0], [12.9, 80.0], [13.0, 80.0], [13.1, 80.0], [13.2, 80.0], [13.3, 80.0], [13.4, 81.0], [13.5, 81.0], [13.6, 81.0], [13.7, 81.0], [13.8, 81.0], [13.9, 81.0], [14.0, 81.0], [14.1, 82.0], [14.2, 82.0], [14.3, 82.0], [14.4, 82.0], [14.5, 82.0], [14.6, 82.0], [14.7, 82.0], [14.8, 82.0], [14.9, 83.0], [15.0, 83.0], [15.1, 83.0], [15.2, 83.0], [15.3, 83.0], [15.4, 83.0], [15.5, 83.0], [15.6, 83.0], [15.7, 84.0], [15.8, 84.0], [15.9, 84.0], [16.0, 84.0], [16.1, 84.0], [16.2, 84.0], [16.3, 84.0], [16.4, 84.0], [16.5, 85.0], [16.6, 85.0], [16.7, 85.0], [16.8, 85.0], [16.9, 85.0], [17.0, 85.0], [17.1, 85.0], [17.2, 85.0], [17.3, 86.0], [17.4, 86.0], [17.5, 86.0], [17.6, 86.0], [17.7, 86.0], [17.8, 86.0], [17.9, 86.0], [18.0, 87.0], [18.1, 87.0], [18.2, 87.0], [18.3, 87.0], [18.4, 87.0], [18.5, 87.0], [18.6, 87.0], [18.7, 87.0], [18.8, 88.0], [18.9, 88.0], [19.0, 88.0], [19.1, 88.0], [19.2, 88.0], [19.3, 88.0], [19.4, 88.0], [19.5, 88.0], [19.6, 89.0], [19.7, 89.0], [19.8, 89.0], [19.9, 89.0], [20.0, 89.0], [20.1, 89.0], [20.2, 89.0], [20.3, 89.0], [20.4, 90.0], [20.5, 90.0], [20.6, 90.0], [20.7, 90.0], [20.8, 90.0], [20.9, 90.0], [21.0, 90.0], [21.1, 90.0], [21.2, 90.0], [21.3, 91.0], [21.4, 91.0], [21.5, 91.0], [21.6, 91.0], [21.7, 91.0], [21.8, 91.0], [21.9, 91.0], [22.0, 91.0], [22.1, 91.0], [22.2, 92.0], [22.3, 92.0], [22.4, 92.0], [22.5, 92.0], [22.6, 92.0], [22.7, 92.0], [22.8, 92.0], [22.9, 92.0], [23.0, 92.0], [23.1, 92.0], [23.2, 93.0], [23.3, 93.0], [23.4, 93.0], [23.5, 93.0], [23.6, 93.0], [23.7, 93.0], [23.8, 93.0], [23.9, 93.0], [24.0, 93.0], [24.1, 93.0], [24.2, 94.0], [24.3, 94.0], [24.4, 94.0], [24.5, 94.0], [24.6, 94.0], [24.7, 94.0], [24.8, 94.0], [24.9, 94.0], [25.0, 94.0], [25.1, 94.0], [25.2, 95.0], [25.3, 95.0], [25.4, 95.0], [25.5, 95.0], [25.6, 95.0], [25.7, 95.0], [25.8, 95.0], [25.9, 95.0], [26.0, 95.0], [26.1, 95.0], [26.2, 95.0], [26.3, 96.0], [26.4, 96.0], [26.5, 96.0], [26.6, 96.0], [26.7, 96.0], [26.8, 96.0], [26.9, 96.0], [27.0, 96.0], [27.1, 96.0], [27.2, 96.0], [27.3, 96.0], [27.4, 97.0], [27.5, 97.0], [27.6, 97.0], [27.7, 97.0], [27.8, 97.0], [27.9, 97.0], [28.0, 97.0], [28.1, 97.0], [28.2, 97.0], [28.3, 97.0], [28.4, 97.0], [28.5, 97.0], [28.6, 98.0], [28.7, 98.0], [28.8, 98.0], [28.9, 98.0], [29.0, 98.0], [29.1, 98.0], [29.2, 98.0], [29.3, 98.0], [29.4, 98.0], [29.5, 98.0], [29.6, 98.0], [29.7, 98.0], [29.8, 99.0], [29.9, 99.0], [30.0, 99.0], [30.1, 99.0], [30.2, 99.0], [30.3, 99.0], [30.4, 99.0], [30.5, 99.0], [30.6, 99.0], [30.7, 99.0], [30.8, 99.0], [30.9, 99.0], [31.0, 100.0], [31.1, 100.0], [31.2, 100.0], [31.3, 100.0], [31.4, 100.0], [31.5, 100.0], [31.6, 100.0], [31.7, 100.0], [31.8, 100.0], [31.9, 100.0], [32.0, 100.0], [32.1, 100.0], [32.2, 101.0], [32.3, 101.0], [32.4, 101.0], [32.5, 101.0], [32.6, 101.0], [32.7, 101.0], [32.8, 101.0], [32.9, 101.0], [33.0, 101.0], [33.1, 101.0], [33.2, 101.0], [33.3, 101.0], [33.4, 102.0], [33.5, 102.0], [33.6, 102.0], [33.7, 102.0], [33.8, 102.0], [33.9, 102.0], [34.0, 102.0], [34.1, 102.0], [34.2, 102.0], [34.3, 102.0], [34.4, 102.0], [34.5, 102.0], [34.6, 103.0], [34.7, 103.0], [34.8, 103.0], [34.9, 103.0], [35.0, 103.0], [35.1, 103.0], [35.2, 103.0], [35.3, 103.0], [35.4, 103.0], [35.5, 103.0], [35.6, 103.0], [35.7, 103.0], [35.8, 103.0], [35.9, 104.0], [36.0, 104.0], [36.1, 104.0], [36.2, 104.0], [36.3, 104.0], [36.4, 104.0], [36.5, 104.0], [36.6, 104.0], [36.7, 104.0], [36.8, 104.0], [36.9, 104.0], [37.0, 105.0], [37.1, 105.0], [37.2, 105.0], [37.3, 105.0], [37.4, 105.0], [37.5, 105.0], [37.6, 105.0], [37.7, 105.0], [37.8, 105.0], [37.9, 105.0], [38.0, 106.0], [38.1, 106.0], [38.2, 106.0], [38.3, 106.0], [38.4, 106.0], [38.5, 106.0], [38.6, 106.0], [38.7, 106.0], [38.8, 106.0], [38.9, 107.0], [39.0, 107.0], [39.1, 107.0], [39.2, 107.0], [39.3, 107.0], [39.4, 107.0], [39.5, 107.0], [39.6, 107.0], [39.7, 107.0], [39.8, 107.0], [39.9, 108.0], [40.0, 108.0], [40.1, 108.0], [40.2, 108.0], [40.3, 108.0], [40.4, 108.0], [40.5, 108.0], [40.6, 108.0], [40.7, 108.0], [40.8, 109.0], [40.9, 109.0], [41.0, 109.0], [41.1, 109.0], [41.2, 109.0], [41.3, 109.0], [41.4, 109.0], [41.5, 109.0], [41.6, 109.0], [41.7, 109.0], [41.8, 110.0], [41.9, 110.0], [42.0, 110.0], [42.1, 110.0], [42.2, 110.0], [42.3, 110.0], [42.4, 110.0], [42.5, 110.0], [42.6, 110.0], [42.7, 110.0], [42.8, 111.0], [42.9, 111.0], [43.0, 111.0], [43.1, 111.0], [43.2, 111.0], [43.3, 111.0], [43.4, 111.0], [43.5, 111.0], [43.6, 111.0], [43.7, 111.0], [43.8, 112.0], [43.9, 112.0], [44.0, 112.0], [44.1, 112.0], [44.2, 112.0], [44.3, 112.0], [44.4, 112.0], [44.5, 112.0], [44.6, 112.0], [44.7, 112.0], [44.8, 112.0], [44.9, 113.0], [45.0, 113.0], [45.1, 113.0], [45.2, 113.0], [45.3, 113.0], [45.4, 113.0], [45.5, 113.0], [45.6, 113.0], [45.7, 113.0], [45.8, 113.0], [45.9, 114.0], [46.0, 114.0], [46.1, 114.0], [46.2, 114.0], [46.3, 114.0], [46.4, 114.0], [46.5, 114.0], [46.6, 114.0], [46.7, 114.0], [46.8, 114.0], [46.9, 114.0], [47.0, 114.0], [47.1, 115.0], [47.2, 115.0], [47.3, 115.0], [47.4, 115.0], [47.5, 115.0], [47.6, 115.0], [47.7, 115.0], [47.8, 115.0], [47.9, 115.0], [48.0, 115.0], [48.1, 115.0], [48.2, 116.0], [48.3, 116.0], [48.4, 116.0], [48.5, 116.0], [48.6, 116.0], [48.7, 116.0], [48.8, 116.0], [48.9, 116.0], [49.0, 116.0], [49.1, 116.0], [49.2, 117.0], [49.3, 117.0], [49.4, 117.0], [49.5, 117.0], [49.6, 117.0], [49.7, 117.0], [49.8, 117.0], [49.9, 117.0], [50.0, 117.0], [50.1, 117.0], [50.2, 118.0], [50.3, 118.0], [50.4, 118.0], [50.5, 118.0], [50.6, 118.0], [50.7, 118.0], [50.8, 118.0], [50.9, 118.0], [51.0, 119.0], [51.1, 119.0], [51.2, 119.0], [51.3, 119.0], [51.4, 119.0], [51.5, 119.0], [51.6, 119.0], [51.7, 119.0], [51.8, 119.0], [51.9, 120.0], [52.0, 120.0], [52.1, 120.0], [52.2, 120.0], [52.3, 120.0], [52.4, 120.0], [52.5, 120.0], [52.6, 120.0], [52.7, 121.0], [52.8, 121.0], [52.9, 121.0], [53.0, 121.0], [53.1, 121.0], [53.2, 121.0], [53.3, 121.0], [53.4, 122.0], [53.5, 122.0], [53.6, 122.0], [53.7, 122.0], [53.8, 122.0], [53.9, 122.0], [54.0, 122.0], [54.1, 123.0], [54.2, 123.0], [54.3, 123.0], [54.4, 123.0], [54.5, 123.0], [54.6, 123.0], [54.7, 124.0], [54.8, 124.0], [54.9, 124.0], [55.0, 124.0], [55.1, 124.0], [55.2, 124.0], [55.3, 124.0], [55.4, 125.0], [55.5, 125.0], [55.6, 125.0], [55.7, 125.0], [55.8, 125.0], [55.9, 125.0], [56.0, 126.0], [56.1, 126.0], [56.2, 126.0], [56.3, 126.0], [56.4, 126.0], [56.5, 126.0], [56.6, 126.0], [56.7, 127.0], [56.8, 127.0], [56.9, 127.0], [57.0, 127.0], [57.1, 127.0], [57.2, 127.0], [57.3, 127.0], [57.4, 128.0], [57.5, 128.0], [57.6, 128.0], [57.7, 128.0], [57.8, 128.0], [57.9, 128.0], [58.0, 128.0], [58.1, 129.0], [58.2, 129.0], [58.3, 129.0], [58.4, 129.0], [58.5, 129.0], [58.6, 129.0], [58.7, 130.0], [58.8, 130.0], [58.9, 130.0], [59.0, 130.0], [59.1, 130.0], [59.2, 130.0], [59.3, 130.0], [59.4, 131.0], [59.5, 131.0], [59.6, 131.0], [59.7, 131.0], [59.8, 131.0], [59.9, 131.0], [60.0, 132.0], [60.1, 132.0], [60.2, 132.0], [60.3, 132.0], [60.4, 132.0], [60.5, 132.0], [60.6, 133.0], [60.7, 133.0], [60.8, 133.0], [60.9, 133.0], [61.0, 133.0], [61.1, 133.0], [61.2, 134.0], [61.3, 134.0], [61.4, 134.0], [61.5, 134.0], [61.6, 134.0], [61.7, 135.0], [61.8, 135.0], [61.9, 135.0], [62.0, 135.0], [62.1, 136.0], [62.2, 136.0], [62.3, 136.0], [62.4, 136.0], [62.5, 136.0], [62.6, 137.0], [62.7, 137.0], [62.8, 137.0], [62.9, 138.0], [63.0, 138.0], [63.1, 138.0], [63.2, 138.0], [63.3, 139.0], [63.4, 139.0], [63.5, 139.0], [63.6, 140.0], [63.7, 140.0], [63.8, 140.0], [63.9, 140.0], [64.0, 141.0], [64.1, 141.0], [64.2, 141.0], [64.3, 141.0], [64.4, 142.0], [64.5, 142.0], [64.6, 142.0], [64.7, 143.0], [64.8, 143.0], [64.9, 143.0], [65.0, 143.0], [65.1, 144.0], [65.2, 144.0], [65.3, 144.0], [65.4, 144.0], [65.5, 145.0], [65.6, 145.0], [65.7, 145.0], [65.8, 146.0], [65.9, 146.0], [66.0, 146.0], [66.1, 146.0], [66.2, 147.0], [66.3, 147.0], [66.4, 147.0], [66.5, 148.0], [66.6, 148.0], [66.7, 148.0], [66.8, 148.0], [66.9, 149.0], [67.0, 149.0], [67.1, 149.0], [67.2, 150.0], [67.3, 150.0], [67.4, 150.0], [67.5, 151.0], [67.6, 151.0], [67.7, 151.0], [67.8, 151.0], [67.9, 152.0], [68.0, 152.0], [68.1, 153.0], [68.2, 153.0], [68.3, 153.0], [68.4, 153.0], [68.5, 154.0], [68.6, 154.0], [68.7, 154.0], [68.8, 155.0], [68.9, 155.0], [69.0, 155.0], [69.1, 156.0], [69.2, 156.0], [69.3, 156.0], [69.4, 157.0], [69.5, 157.0], [69.6, 157.0], [69.7, 158.0], [69.8, 158.0], [69.9, 159.0], [70.0, 159.0], [70.1, 159.0], [70.2, 160.0], [70.3, 160.0], [70.4, 161.0], [70.5, 161.0], [70.6, 161.0], [70.7, 162.0], [70.8, 162.0], [70.9, 162.0], [71.0, 163.0], [71.1, 163.0], [71.2, 163.0], [71.3, 164.0], [71.4, 164.0], [71.5, 165.0], [71.6, 165.0], [71.7, 165.0], [71.8, 166.0], [71.9, 166.0], [72.0, 166.0], [72.1, 167.0], [72.2, 167.0], [72.3, 167.0], [72.4, 168.0], [72.5, 168.0], [72.6, 169.0], [72.7, 169.0], [72.8, 170.0], [72.9, 170.0], [73.0, 170.0], [73.1, 171.0], [73.2, 171.0], [73.3, 172.0], [73.4, 172.0], [73.5, 173.0], [73.6, 173.0], [73.7, 173.0], [73.8, 174.0], [73.9, 174.0], [74.0, 175.0], [74.1, 175.0], [74.2, 176.0], [74.3, 176.0], [74.4, 176.0], [74.5, 177.0], [74.6, 177.0], [74.7, 178.0], [74.8, 178.0], [74.9, 179.0], [75.0, 179.0], [75.1, 179.0], [75.2, 180.0], [75.3, 180.0], [75.4, 181.0], [75.5, 181.0], [75.6, 182.0], [75.7, 182.0], [75.8, 183.0], [75.9, 183.0], [76.0, 184.0], [76.1, 184.0], [76.2, 185.0], [76.3, 185.0], [76.4, 186.0], [76.5, 186.0], [76.6, 187.0], [76.7, 188.0], [76.8, 188.0], [76.9, 189.0], [77.0, 189.0], [77.1, 189.0], [77.2, 190.0], [77.3, 190.0], [77.4, 191.0], [77.5, 191.0], [77.6, 192.0], [77.7, 193.0], [77.8, 193.0], [77.9, 194.0], [78.0, 194.0], [78.1, 195.0], [78.2, 195.0], [78.3, 196.0], [78.4, 196.0], [78.5, 197.0], [78.6, 197.0], [78.7, 198.0], [78.8, 199.0], [78.9, 200.0], [79.0, 200.0], [79.1, 201.0], [79.2, 202.0], [79.3, 203.0], [79.4, 203.0], [79.5, 204.0], [79.6, 205.0], [79.7, 206.0], [79.8, 207.0], [79.9, 208.0], [80.0, 208.0], [80.1, 210.0], [80.2, 211.0], [80.3, 212.0], [80.4, 213.0], [80.5, 215.0], [80.6, 216.0], [80.7, 217.0], [80.8, 217.0], [80.9, 218.0], [81.0, 219.0], [81.1, 220.0], [81.2, 221.0], [81.3, 222.0], [81.4, 224.0], [81.5, 225.0], [81.6, 226.0], [81.7, 227.0], [81.8, 228.0], [81.9, 229.0], [82.0, 230.0], [82.1, 230.0], [82.2, 231.0], [82.3, 232.0], [82.4, 233.0], [82.5, 234.0], [82.6, 235.0], [82.7, 236.0], [82.8, 237.0], [82.9, 238.0], [83.0, 239.0], [83.1, 240.0], [83.2, 240.0], [83.3, 242.0], [83.4, 243.0], [83.5, 244.0], [83.6, 245.0], [83.7, 246.0], [83.8, 248.0], [83.9, 249.0], [84.0, 250.0], [84.1, 251.0], [84.2, 252.0], [84.3, 253.0], [84.4, 254.0], [84.5, 255.0], [84.6, 256.0], [84.7, 257.0], [84.8, 258.0], [84.9, 260.0], [85.0, 262.0], [85.1, 263.0], [85.2, 264.0], [85.3, 266.0], [85.4, 267.0], [85.5, 269.0], [85.6, 270.0], [85.7, 272.0], [85.8, 273.0], [85.9, 274.0], [86.0, 276.0], [86.1, 278.0], [86.2, 279.0], [86.3, 280.0], [86.4, 281.0], [86.5, 282.0], [86.6, 283.0], [86.7, 284.0], [86.8, 285.0], [86.9, 286.0], [87.0, 288.0], [87.1, 289.0], [87.2, 290.0], [87.3, 291.0], [87.4, 292.0], [87.5, 293.0], [87.6, 294.0], [87.7, 296.0], [87.8, 297.0], [87.9, 299.0], [88.0, 300.0], [88.1, 303.0], [88.2, 305.0], [88.3, 311.0], [88.4, 314.0], [88.5, 317.0], [88.6, 319.0], [88.7, 321.0], [88.8, 323.0], [88.9, 325.0], [89.0, 327.0], [89.1, 330.0], [89.2, 332.0], [89.3, 336.0], [89.4, 339.0], [89.5, 341.0], [89.6, 342.0], [89.7, 343.0], [89.8, 345.0], [89.9, 346.0], [90.0, 347.0], [90.1, 349.0], [90.2, 350.0], [90.3, 352.0], [90.4, 354.0], [90.5, 358.0], [90.6, 364.0], [90.7, 366.0], [90.8, 369.0], [90.9, 372.0], [91.0, 376.0], [91.1, 379.0], [91.2, 381.0], [91.3, 383.0], [91.4, 385.0], [91.5, 392.0], [91.6, 399.0], [91.7, 403.0], [91.8, 409.0], [91.9, 412.0], [92.0, 416.0], [92.1, 418.0], [92.2, 421.0], [92.3, 423.0], [92.4, 425.0], [92.5, 427.0], [92.6, 429.0], [92.7, 431.0], [92.8, 433.0], [92.9, 438.0], [93.0, 442.0], [93.1, 448.0], [93.2, 456.0], [93.3, 460.0], [93.4, 463.0], [93.5, 467.0], [93.6, 471.0], [93.7, 474.0], [93.8, 477.0], [93.9, 480.0], [94.0, 482.0], [94.1, 484.0], [94.2, 487.0], [94.3, 490.0], [94.4, 493.0], [94.5, 496.0], [94.6, 498.0], [94.7, 500.0], [94.8, 502.0], [94.9, 504.0], [95.0, 506.0], [95.1, 508.0], [95.2, 510.0], [95.3, 512.0], [95.4, 514.0], [95.5, 516.0], [95.6, 517.0], [95.7, 519.0], [95.8, 521.0], [95.9, 524.0], [96.0, 526.0], [96.1, 528.0], [96.2, 531.0], [96.3, 533.0], [96.4, 536.0], [96.5, 539.0], [96.6, 541.0], [96.7, 545.0], [96.8, 549.0], [96.9, 551.0], [97.0, 555.0], [97.1, 558.0], [97.2, 562.0], [97.3, 566.0], [97.4, 572.0], [97.5, 577.0], [97.6, 584.0], [97.7, 588.0], [97.8, 593.0], [97.9, 597.0], [98.0, 601.0], [98.1, 604.0], [98.2, 608.0], [98.3, 612.0], [98.4, 618.0], [98.5, 628.0], [98.6, 651.0], [98.7, 671.0], [98.8, 714.0], [98.9, 730.0], [99.0, 766.0], [99.1, 778.0], [99.2, 886.0], [99.3, 933.0], [99.4, 1088.0], [99.5, 1151.0], [99.6, 1486.0], [99.7, 1612.0], [99.8, 1791.0], [99.9, 2274.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
        getOptions: function() {
            return {
                series: {
                    points: { show: false }
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentiles'
                },
                xaxis: {
                    tickDecimals: 1,
                    axisLabel: "Percentiles",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Percentile value in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : %x.2 percentile was %y ms"
                },
                selection: { mode: "xy" },
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentiles"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesPercentiles"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesPercentiles"), dataset, prepareOverviewOptions(options));
        }
};

/**
 * @param elementId Id of element where we display message
 */
function setEmptyGraph(elementId) {
    $(function() {
        $(elementId).text("No graph series with filter="+seriesFilter);
    });
}

// Response times percentiles
function refreshResponseTimePercentiles() {
    var infos = responseTimePercentilesInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimePercentiles");
        return;
    }
    if (isGraph($("#flotResponseTimesPercentiles"))){
        infos.createGraph();
    } else {
        var choiceContainer = $("#choicesResponseTimePercentiles");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesPercentiles", "#overviewResponseTimesPercentiles");
        $('#bodyResponseTimePercentiles .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimeDistributionInfos = {
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 21702.0, "series": [{"data": [[0.0, 14026.0], [600.0, 368.0], [700.0, 165.0], [800.0, 62.0], [900.0, 50.0], [1000.0, 23.0], [1100.0, 44.0], [1200.0, 6.0], [1300.0, 4.0], [1400.0, 38.0], [1500.0, 14.0], [100.0, 21702.0], [1600.0, 23.0], [1700.0, 40.0], [1800.0, 4.0], [1900.0, 17.0], [2000.0, 10.0], [2100.0, 4.0], [2200.0, 7.0], [2300.0, 17.0], [2400.0, 8.0], [2500.0, 4.0], [2600.0, 2.0], [2700.0, 2.0], [2800.0, 1.0], [3100.0, 1.0], [200.0, 4101.0], [3700.0, 1.0], [4300.0, 1.0], [300.0, 1657.0], [5100.0, 6.0], [4900.0, 1.0], [5200.0, 1.0], [400.0, 1375.0], [500.0, 1499.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 5200.0, "title": "Response Time Distribution"}},
        getOptions: function() {
            var granularity = this.data.result.granularity;
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    barWidth: this.data.result.granularity
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " responses for " + label + " were between " + xval + " and " + (xval + granularity) + " ms";
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimeDistribution"), prepareData(data.result.series, $("#choicesResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshResponseTimeDistribution() {
    var infos = responseTimeDistributionInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeDistribution");
        return;
    }
    if (isGraph($("#flotResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var syntheticResponseTimeDistributionInfos = {
        data: {"result": {"minY": 45284.0, "minX": 3.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 45284.0, "series": [{"data": [], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [[3.0, 45284.0]], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 3.0, "title": "Synthetic Response Times Distribution"}},
        getOptions: function() {
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendSyntheticResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times ranges",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                    tickLength:0,
                    min:-0.5,
                    max:3.5
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    align: "center",
                    barWidth: 0.25,
                    fill:.75
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " " + label;
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            options.xaxis.ticks = data.result.ticks;
            $.plot($("#flotSyntheticResponseTimeDistribution"), prepareData(data.result.series, $("#choicesSyntheticResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshSyntheticResponseTimeDistribution() {
    var infos = syntheticResponseTimeDistributionInfos;
    prepareSeries(infos.data, true);
    if (isGraph($("#flotSyntheticResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerSyntheticResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var activeThreadsOverTimeInfos = {
        data: {"result": {"minY": 39.31977052074129, "minX": 1.77360594E12, "maxY": 50.0, "series": [{"data": [[1.773606E12, 50.0], [1.77360606E12, 50.0], [1.77360594E12, 39.31977052074129], [1.77360612E12, 48.8032786885246]], "isOverall": false, "label": "Concurrent Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360612E12, "title": "Active Threads Over Time"}},
        getOptions: function() {
            return {
                series: {
                    stack: true,
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 6,
                    show: true,
                    container: '#legendActiveThreadsOverTime'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                selection: {
                    mode: 'xy'
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : At %x there were %y active threads"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesActiveThreadsOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotActiveThreadsOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewActiveThreadsOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Active Threads Over Time
function refreshActiveThreadsOverTime(fixTimestamps) {
    var infos = activeThreadsOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotActiveThreadsOverTime"))) {
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesActiveThreadsOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotActiveThreadsOverTime", "#overviewActiveThreadsOverTime");
        $('#footerActiveThreadsOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var timeVsThreadsInfos = {
        data: {"result": {"minY": 45.5142857142857, "minX": 3.0, "maxY": 356.28877005347584, "series": [{"data": [[32.0, 78.85398230088487], [33.0, 77.92653061224486], [34.0, 136.45454545454555], [35.0, 102.08421052631577], [36.0, 117.13939393939397], [37.0, 99.5972850678734], [38.0, 97.11715481171544], [39.0, 134.90967741935484], [40.0, 84.98936170212767], [41.0, 81.67132867132868], [42.0, 89.01818181818182], [43.0, 98.06967213114758], [44.0, 101.03305785123962], [45.0, 104.39430894308951], [46.0, 140.8538011695906], [47.0, 157.82352941176467], [48.0, 113.02510460251054], [49.0, 172.49390243902425], [3.0, 271.0], [50.0, 188.6082088576145], [4.0, 130.25], [5.0, 47.36206896551724], [6.0, 45.5142857142857], [7.0, 63.20512820512819], [13.0, 266.09999999999997], [14.0, 234.0], [16.0, 356.28877005347584], [17.0, 66.48648648648651], [18.0, 103.95876288659794], [19.0, 108.42105263157897], [20.0, 79.46043165467624], [21.0, 90.75000000000001], [22.0, 60.65365853658536], [23.0, 58.212669683257914], [24.0, 59.02631578947365], [25.0, 61.63749999999999], [26.0, 65.84255319148939], [27.0, 66.50446428571426], [28.0, 67.67768595041323], [29.0, 84.18497109826589], [30.0, 143.0588235294117], [31.0, 86.16956521739128]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}, {"data": [[47.30847539969984, 174.81978182139247]], "isOverall": false, "label": "POST /api/v1/beta/translate-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 50.0, "title": "Time VS Threads"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: { noColumns: 2,show: true, container: '#legendTimeVsThreads' },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s: At %x.2 active threads, Average response time was %y.2 ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesTimeVsThreads"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotTimesVsThreads"), dataset, options);
            // setup overview
            $.plot($("#overviewTimesVsThreads"), dataset, prepareOverviewOptions(options));
        }
};

// Time vs threads
function refreshTimeVsThreads(){
    var infos = timeVsThreadsInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTimeVsThreads");
        return;
    }
    if(isGraph($("#flotTimesVsThreads"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTimeVsThreads");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTimesVsThreads", "#overviewTimesVsThreads");
        $('#footerTimeVsThreads .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var bytesThroughputOverTimeInfos = {
        data : {"result": {"minY": 2305.8, "minX": 1.77360594E12, "maxY": 179981.78333333333, "series": [{"data": [[1.773606E12, 39850.28333333333], [1.77360606E12, 71085.68333333333], [1.77360594E12, 38832.833333333336], [1.77360612E12, 2305.8]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.773606E12, 96852.65], [1.77360606E12, 179981.78333333333], [1.77360594E12, 94144.83333333333], [1.77360612E12, 6136.6]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360612E12, "title": "Bytes Throughput Over Time"}},
        getOptions : function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity) ,
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Bytes / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendBytesThroughputOverTime'
                },
                selection: {
                    mode: "xy"
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y"
                }
            };
        },
        createGraph : function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesBytesThroughputOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotBytesThroughputOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewBytesThroughputOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Bytes throughput Over Time
function refreshBytesThroughputOverTime(fixTimestamps) {
    var infos = bytesThroughputOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotBytesThroughputOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesBytesThroughputOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotBytesThroughputOverTime", "#overviewBytesThroughputOverTime");
        $('#footerBytesThroughputOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimesOverTimeInfos = {
        data: {"result": {"minY": 133.8439890583697, "minX": 1.77360594E12, "maxY": 242.2503218055434, "series": [{"data": [[1.773606E12, 242.2503218055434], [1.77360606E12, 133.8439890583697], [1.77360594E12, 183.16381288614218], [1.77360612E12, 179.6024590163936]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360612E12, "title": "Response Time Over Time"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average response time was %y ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Times Over Time
function refreshResponseTimeOverTime(fixTimestamps) {
    var infos = responseTimesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotResponseTimesOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesOverTime", "#overviewResponseTimesOverTime");
        $('#footerResponseTimesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var latenciesOverTimeInfos = {
        data: {"result": {"minY": 133.65079512263063, "minX": 1.77360594E12, "maxY": 241.2799279155578, "series": [{"data": [[1.773606E12, 241.2799279155578], [1.77360606E12, 133.65079512263063], [1.77360594E12, 183.0965578111208], [1.77360612E12, 179.59699453551912]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360612E12, "title": "Latencies Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response latencies in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendLatenciesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average latency was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesLatenciesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotLatenciesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewLatenciesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Latencies Over Time
function refreshLatenciesOverTime(fixTimestamps) {
    var infos = latenciesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyLatenciesOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotLatenciesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesLatenciesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotLatenciesOverTime", "#overviewLatenciesOverTime");
        $('#footerLatenciesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var connectTimeOverTimeInfos = {
        data: {"result": {"minY": 0.0, "minX": 1.77360594E12, "maxY": 0.06954986760812013, "series": [{"data": [[1.773606E12, 0.018278554878572124], [1.77360606E12, 0.009736195465714735], [1.77360594E12, 0.06954986760812013], [1.77360612E12, 0.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360612E12, "title": "Connect Time Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getConnectTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average Connect Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendConnectTimeOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average connect time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesConnectTimeOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotConnectTimeOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewConnectTimeOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Connect Time Over Time
function refreshConnectTimeOverTime(fixTimestamps) {
    var infos = connectTimeOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyConnectTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotConnectTimeOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesConnectTimeOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotConnectTimeOverTime", "#overviewConnectTimeOverTime");
        $('#footerConnectTimeOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var responseTimePercentilesOverTimeInfos = {
        data: {"result": {"minY": 1.7976931348623157E308, "minX": 1.7976931348623157E308, "maxY": 4.9E-324, "series": [{"data": [], "isOverall": false, "label": "Max", "isController": false}, {"data": [], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [], "isOverall": false, "label": "95th percentile", "isController": false}, {"data": [], "isOverall": false, "label": "Min", "isController": false}, {"data": [], "isOverall": false, "label": "Median", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 4.9E-324, "title": "Response Time Percentiles Over Time (successful requests only)"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Response Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentilesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Response time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentilesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimePercentilesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimePercentilesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Time Percentiles Over Time
function refreshResponseTimePercentilesOverTime(fixTimestamps) {
    var infos = responseTimePercentilesOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotResponseTimePercentilesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimePercentilesOverTime", "#overviewResponseTimePercentilesOverTime");
        $('#footerResponseTimePercentilesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var responseTimeVsRequestInfos = {
    data: {"result": {"minY": 25.0, "minX": 15.0, "maxY": 1715.5, "series": [{"data": [[15.0, 1137.0], [18.0, 28.0], [26.0, 1715.5], [29.0, 577.0], [35.0, 111.0], [40.0, 25.0], [41.0, 377.5], [50.0, 473.5], [67.0, 611.0], [74.0, 605.0], [76.0, 544.0], [79.0, 137.0], [77.0, 485.0], [83.0, 595.0], [87.0, 65.0], [91.0, 125.0], [90.0, 339.0], [95.0, 84.0], [98.0, 276.0], [100.0, 515.0], [101.0, 106.0], [103.0, 547.0], [106.0, 419.5], [105.0, 139.0], [109.0, 488.0], [117.0, 415.0], [118.0, 204.0], [120.0, 472.5], [123.0, 429.0], [124.0, 463.5], [130.0, 379.0], [133.0, 384.5], [150.0, 282.0], [145.0, 332.0], [151.0, 227.0], [158.0, 108.0], [154.0, 301.0], [157.0, 84.0], [167.0, 258.0], [165.0, 202.0], [172.0, 290.0], [200.0, 213.5], [211.0, 219.0], [212.0, 185.0], [213.0, 232.0], [217.0, 237.0], [225.0, 201.0], [239.0, 71.0], [233.0, 168.0], [238.0, 118.0], [240.0, 128.0], [250.0, 190.0], [254.0, 179.0], [264.0, 52.0], [259.0, 194.0], [270.0, 104.0], [280.0, 131.0], [272.0, 140.5], [277.0, 129.0], [281.0, 135.0], [289.0, 152.0], [303.0, 126.0], [300.0, 143.0], [301.0, 131.0], [311.0, 66.0], [314.0, 93.0], [315.0, 93.0], [310.0, 143.0], [309.0, 104.0], [312.0, 141.0], [307.0, 65.0], [331.0, 85.0], [329.0, 118.0], [328.0, 101.5], [327.0, 155.0], [339.0, 125.0], [349.0, 89.0], [350.0, 127.0], [351.0, 134.0], [340.0, 136.5], [366.0, 55.0], [355.0, 114.0], [357.0, 106.0], [356.0, 119.0], [359.0, 119.0], [363.0, 135.0], [367.0, 127.0], [368.0, 68.0], [379.0, 74.0], [383.0, 104.0], [373.0, 137.0], [380.0, 120.0], [378.0, 99.0], [388.0, 58.5], [385.0, 105.0], [399.0, 106.0], [387.0, 126.0], [386.0, 112.0], [397.0, 103.0], [400.0, 123.0], [409.0, 111.0], [412.0, 114.0], [408.0, 114.5], [401.0, 110.0], [407.0, 111.0], [405.0, 109.0], [402.0, 109.0], [424.0, 101.5], [428.0, 112.0], [419.0, 110.0], [421.0, 118.0], [435.0, 91.0], [447.0, 97.0], [440.0, 114.0], [437.0, 106.0], [455.0, 107.0], [465.0, 74.0], [479.0, 101.0], [476.0, 104.0], [483.0, 97.0], [501.0, 92.0], [506.0, 93.0], [500.0, 94.5], [514.0, 99.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 514.0, "title": "Response Time Vs Request"}},
    getOptions: function() {
        return {
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Response Time in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: {
                noColumns: 2,
                show: true,
                container: '#legendResponseTimeVsRequest'
            },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median response time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesResponseTimeVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotResponseTimeVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewResponseTimeVsRequest"), dataset, prepareOverviewOptions(options));

    }
};

// Response Time vs Request
function refreshResponseTimeVsRequest() {
    var infos = responseTimeVsRequestInfos;
    prepareSeries(infos.data);
    if (isGraph($("#flotResponseTimeVsRequest"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeVsRequest");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimeVsRequest", "#overviewResponseTimeVsRequest");
        $('#footerResponseRimeVsRequest .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var latenciesVsRequestInfos = {
    data: {"result": {"minY": 0.0, "minX": 15.0, "maxY": 1715.5, "series": [{"data": [[15.0, 1137.0], [18.0, 21.0], [26.0, 1715.5], [29.0, 577.0], [35.0, 111.0], [40.0, 24.5], [41.0, 377.5], [50.0, 473.5], [67.0, 611.0], [74.0, 605.0], [76.0, 544.0], [79.0, 137.0], [77.0, 485.0], [83.0, 595.0], [87.0, 65.0], [91.0, 125.0], [90.0, 339.0], [95.0, 84.0], [98.0, 276.0], [100.0, 515.0], [101.0, 106.0], [103.0, 547.0], [106.0, 0.0], [105.0, 139.0], [109.0, 488.0], [117.0, 415.0], [118.0, 204.0], [120.0, 472.5], [123.0, 429.0], [124.0, 463.5], [130.0, 379.0], [133.0, 384.5], [150.0, 282.0], [145.0, 332.0], [151.0, 227.0], [158.0, 108.0], [154.0, 301.0], [157.0, 84.0], [167.0, 258.0], [165.0, 179.0], [172.0, 290.0], [200.0, 213.5], [211.0, 219.0], [212.0, 185.0], [213.0, 232.0], [217.0, 237.0], [225.0, 201.0], [239.0, 71.0], [233.0, 168.0], [238.0, 118.0], [240.0, 128.0], [250.0, 190.0], [254.0, 179.0], [264.0, 52.0], [259.0, 194.0], [270.0, 104.0], [280.0, 131.0], [272.0, 140.5], [277.0, 129.0], [281.0, 135.0], [289.0, 152.0], [303.0, 126.0], [300.0, 143.0], [301.0, 131.0], [311.0, 66.0], [314.0, 93.0], [315.0, 93.0], [310.0, 143.0], [309.0, 104.0], [312.0, 141.0], [307.0, 65.0], [331.0, 85.0], [329.0, 118.0], [328.0, 101.5], [327.0, 155.0], [339.0, 125.0], [349.0, 89.0], [350.0, 127.0], [351.0, 134.0], [340.0, 136.5], [366.0, 54.5], [355.0, 114.0], [357.0, 106.0], [356.0, 119.0], [359.0, 119.0], [363.0, 135.0], [367.0, 127.0], [368.0, 67.5], [379.0, 74.0], [383.0, 104.0], [373.0, 137.0], [380.0, 120.0], [378.0, 99.0], [388.0, 58.5], [385.0, 105.0], [399.0, 106.0], [387.0, 126.0], [386.0, 112.0], [397.0, 103.0], [400.0, 123.0], [409.0, 111.0], [412.0, 114.0], [408.0, 114.5], [401.0, 110.0], [407.0, 111.0], [405.0, 109.0], [402.0, 109.0], [424.0, 101.5], [428.0, 112.0], [419.0, 110.0], [421.0, 118.0], [435.0, 91.0], [447.0, 97.0], [440.0, 114.0], [437.0, 106.0], [455.0, 107.0], [465.0, 74.0], [479.0, 101.0], [476.0, 104.0], [483.0, 97.0], [501.0, 92.0], [506.0, 93.0], [500.0, 94.5], [514.0, 99.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 514.0, "title": "Latencies Vs Request"}},
    getOptions: function() {
        return{
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Latency in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: { noColumns: 2,show: true, container: '#legendLatencyVsRequest' },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median Latency time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesLatencyVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotLatenciesVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewLatenciesVsRequest"), dataset, prepareOverviewOptions(options));
    }
};

// Latencies vs Request
function refreshLatenciesVsRequest() {
        var infos = latenciesVsRequestInfos;
        prepareSeries(infos.data);
        if(isGraph($("#flotLatenciesVsRequest"))){
            infos.createGraph();
        }else{
            var choiceContainer = $("#choicesLatencyVsRequest");
            createLegend(choiceContainer, infos);
            infos.createGraph();
            setGraphZoomable("#flotLatenciesVsRequest", "#overviewLatenciesVsRequest");
            $('#footerLatenciesVsRequest .legendColorBox > div').each(function(i){
                $(this).clone().prependTo(choiceContainer.find("li").eq(i));
            });
        }
};

var hitsPerSecondInfos = {
        data: {"result": {"minY": 11.583333333333334, "minX": 1.77360594E12, "maxY": 360.1, "series": [{"data": [[1.773606E12, 193.38333333333333], [1.77360606E12, 360.1], [1.77360594E12, 189.66666666666666], [1.77360612E12, 11.583333333333334]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360612E12, "title": "Hits Per Second"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of hits / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendHitsPerSecond"
                },
                selection: {
                    mode : 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y.2 hits/sec"
                }
            };
        },
        createGraph: function createGraph() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesHitsPerSecond"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotHitsPerSecond"), dataset, options);
            // setup overview
            $.plot($("#overviewHitsPerSecond"), dataset, prepareOverviewOptions(options));
        }
};

// Hits per second
function refreshHitsPerSecond(fixTimestamps) {
    var infos = hitsPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if (isGraph($("#flotHitsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesHitsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotHitsPerSecond", "#overviewHitsPerSecond");
        $('#footerHitsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var codesPerSecondInfos = {
        data: {"result": {"minY": 1.6666666666666667, "minX": 1.77360594E12, "maxY": 356.15, "series": [{"data": [[1.773606E12, 1.6666666666666667], [1.77360606E12, 1.6666666666666667], [1.77360594E12, 1.6666666666666667]], "isOverall": false, "label": "500", "isController": false}, {"data": [[1.773606E12, 1.6666666666666667], [1.77360606E12, 1.6666666666666667], [1.77360594E12, 1.6666666666666667]], "isOverall": false, "label": "Non HTTP response code: org.apache.http.NoHttpResponseException", "isController": false}, {"data": [[1.773606E12, 190.88333333333333], [1.77360606E12, 356.15], [1.77360594E12, 185.5], [1.77360612E12, 12.2]], "isOverall": false, "label": "429", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360612E12, "title": "Codes Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendCodesPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "Number of Response Codes %s at %x was %y.2 responses / sec"
                }
            };
        },
    createGraph: function() {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesCodesPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotCodesPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewCodesPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Codes per second
function refreshCodesPerSecond(fixTimestamps) {
    var infos = codesPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotCodesPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesCodesPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotCodesPerSecond", "#overviewCodesPerSecond");
        $('#footerCodesPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var transactionsPerSecondInfos = {
        data: {"result": {"minY": 12.2, "minX": 1.77360594E12, "maxY": 359.48333333333335, "series": [{"data": [[1.773606E12, 194.21666666666667], [1.77360606E12, 359.48333333333335], [1.77360594E12, 188.83333333333334], [1.77360612E12, 12.2]], "isOverall": false, "label": "POST /api/v1/beta/translate-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360612E12, "title": "Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTransactionsPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                }
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTransactionsPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTransactionsPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewTransactionsPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Transactions per second
function refreshTransactionsPerSecond(fixTimestamps) {
    var infos = transactionsPerSecondInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTransactionsPerSecond");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotTransactionsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTransactionsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTransactionsPerSecond", "#overviewTransactionsPerSecond");
        $('#footerTransactionsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var totalTPSInfos = {
        data: {"result": {"minY": 12.2, "minX": 1.77360594E12, "maxY": 359.48333333333335, "series": [{"data": [], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [[1.773606E12, 194.21666666666667], [1.77360606E12, 359.48333333333335], [1.77360594E12, 188.83333333333334], [1.77360612E12, 12.2]], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360612E12, "title": "Total Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTotalTPS"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                },
                colors: ["#9ACD32", "#FF6347"]
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTotalTPS"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTotalTPS"), dataset, options);
        // setup overview
        $.plot($("#overviewTotalTPS"), dataset, prepareOverviewOptions(options));
    }
};

// Total Transactions per second
function refreshTotalTPS(fixTimestamps) {
    var infos = totalTPSInfos;
    // We want to ignore seriesFilter
    prepareSeries(infos.data, false, true);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 7200000);
    }
    if(isGraph($("#flotTotalTPS"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTotalTPS");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTotalTPS", "#overviewTotalTPS");
        $('#footerTotalTPS .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

// Collapse the graph matching the specified DOM element depending the collapsed
// status
function collapse(elem, collapsed){
    if(collapsed){
        $(elem).parent().find(".fa-chevron-up").removeClass("fa-chevron-up").addClass("fa-chevron-down");
    } else {
        $(elem).parent().find(".fa-chevron-down").removeClass("fa-chevron-down").addClass("fa-chevron-up");
        if (elem.id == "bodyBytesThroughputOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshBytesThroughputOverTime(true);
            }
            document.location.href="#bytesThroughputOverTime";
        } else if (elem.id == "bodyLatenciesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesOverTime(true);
            }
            document.location.href="#latenciesOverTime";
        } else if (elem.id == "bodyCustomGraph") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCustomGraph(true);
            }
            document.location.href="#responseCustomGraph";
        } else if (elem.id == "bodyConnectTimeOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshConnectTimeOverTime(true);
            }
            document.location.href="#connectTimeOverTime";
        } else if (elem.id == "bodyResponseTimePercentilesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimePercentilesOverTime(true);
            }
            document.location.href="#responseTimePercentilesOverTime";
        } else if (elem.id == "bodyResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeDistribution();
            }
            document.location.href="#responseTimeDistribution" ;
        } else if (elem.id == "bodySyntheticResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshSyntheticResponseTimeDistribution();
            }
            document.location.href="#syntheticResponseTimeDistribution" ;
        } else if (elem.id == "bodyActiveThreadsOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshActiveThreadsOverTime(true);
            }
            document.location.href="#activeThreadsOverTime";
        } else if (elem.id == "bodyTimeVsThreads") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTimeVsThreads();
            }
            document.location.href="#timeVsThreads" ;
        } else if (elem.id == "bodyCodesPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCodesPerSecond(true);
            }
            document.location.href="#codesPerSecond";
        } else if (elem.id == "bodyTransactionsPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTransactionsPerSecond(true);
            }
            document.location.href="#transactionsPerSecond";
        } else if (elem.id == "bodyTotalTPS") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTotalTPS(true);
            }
            document.location.href="#totalTPS";
        } else if (elem.id == "bodyResponseTimeVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeVsRequest();
            }
            document.location.href="#responseTimeVsRequest";
        } else if (elem.id == "bodyLatenciesVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesVsRequest();
            }
            document.location.href="#latencyVsRequest";
        }
    }
}

/*
 * Activates or deactivates all series of the specified graph (represented by id parameter)
 * depending on checked argument.
 */
function toggleAll(id, checked){
    var placeholder = document.getElementById(id);

    var cases = $(placeholder).find(':checkbox');
    cases.prop('checked', checked);
    $(cases).parent().children().children().toggleClass("legend-disabled", !checked);

    var choiceContainer;
    if ( id == "choicesBytesThroughputOverTime"){
        choiceContainer = $("#choicesBytesThroughputOverTime");
        refreshBytesThroughputOverTime(false);
    } else if(id == "choicesResponseTimesOverTime"){
        choiceContainer = $("#choicesResponseTimesOverTime");
        refreshResponseTimeOverTime(false);
    }else if(id == "choicesResponseCustomGraph"){
        choiceContainer = $("#choicesResponseCustomGraph");
        refreshCustomGraph(false);
    } else if ( id == "choicesLatenciesOverTime"){
        choiceContainer = $("#choicesLatenciesOverTime");
        refreshLatenciesOverTime(false);
    } else if ( id == "choicesConnectTimeOverTime"){
        choiceContainer = $("#choicesConnectTimeOverTime");
        refreshConnectTimeOverTime(false);
    } else if ( id == "choicesResponseTimePercentilesOverTime"){
        choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        refreshResponseTimePercentilesOverTime(false);
    } else if ( id == "choicesResponseTimePercentiles"){
        choiceContainer = $("#choicesResponseTimePercentiles");
        refreshResponseTimePercentiles();
    } else if(id == "choicesActiveThreadsOverTime"){
        choiceContainer = $("#choicesActiveThreadsOverTime");
        refreshActiveThreadsOverTime(false);
    } else if ( id == "choicesTimeVsThreads"){
        choiceContainer = $("#choicesTimeVsThreads");
        refreshTimeVsThreads();
    } else if ( id == "choicesSyntheticResponseTimeDistribution"){
        choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        refreshSyntheticResponseTimeDistribution();
    } else if ( id == "choicesResponseTimeDistribution"){
        choiceContainer = $("#choicesResponseTimeDistribution");
        refreshResponseTimeDistribution();
    } else if ( id == "choicesHitsPerSecond"){
        choiceContainer = $("#choicesHitsPerSecond");
        refreshHitsPerSecond(false);
    } else if(id == "choicesCodesPerSecond"){
        choiceContainer = $("#choicesCodesPerSecond");
        refreshCodesPerSecond(false);
    } else if ( id == "choicesTransactionsPerSecond"){
        choiceContainer = $("#choicesTransactionsPerSecond");
        refreshTransactionsPerSecond(false);
    } else if ( id == "choicesTotalTPS"){
        choiceContainer = $("#choicesTotalTPS");
        refreshTotalTPS(false);
    } else if ( id == "choicesResponseTimeVsRequest"){
        choiceContainer = $("#choicesResponseTimeVsRequest");
        refreshResponseTimeVsRequest();
    } else if ( id == "choicesLatencyVsRequest"){
        choiceContainer = $("#choicesLatencyVsRequest");
        refreshLatenciesVsRequest();
    }
    var color = checked ? "black" : "#818181";
    if(choiceContainer != null) {
        choiceContainer.find("label").each(function(){
            this.style.color = color;
        });
    }
}

