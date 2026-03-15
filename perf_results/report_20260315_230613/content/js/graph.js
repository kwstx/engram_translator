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
        data: {"result": {"minY": 3.0, "minX": 0.0, "maxY": 8052.0, "series": [{"data": [[0.0, 3.0], [0.1, 5.0], [0.2, 6.0], [0.3, 7.0], [0.4, 8.0], [0.5, 8.0], [0.6, 9.0], [0.7, 9.0], [0.8, 10.0], [0.9, 11.0], [1.0, 11.0], [1.1, 12.0], [1.2, 12.0], [1.3, 13.0], [1.4, 14.0], [1.5, 14.0], [1.6, 15.0], [1.7, 16.0], [1.8, 16.0], [1.9, 17.0], [2.0, 18.0], [2.1, 18.0], [2.2, 19.0], [2.3, 19.0], [2.4, 20.0], [2.5, 21.0], [2.6, 21.0], [2.7, 22.0], [2.8, 23.0], [2.9, 23.0], [3.0, 24.0], [3.1, 24.0], [3.2, 24.0], [3.3, 24.0], [3.4, 25.0], [3.5, 25.0], [3.6, 25.0], [3.7, 25.0], [3.8, 25.0], [3.9, 25.0], [4.0, 25.0], [4.1, 25.0], [4.2, 26.0], [4.3, 26.0], [4.4, 26.0], [4.5, 26.0], [4.6, 26.0], [4.7, 26.0], [4.8, 26.0], [4.9, 26.0], [5.0, 26.0], [5.1, 26.0], [5.2, 26.0], [5.3, 26.0], [5.4, 26.0], [5.5, 26.0], [5.6, 26.0], [5.7, 26.0], [5.8, 26.0], [5.9, 27.0], [6.0, 27.0], [6.1, 27.0], [6.2, 27.0], [6.3, 27.0], [6.4, 27.0], [6.5, 27.0], [6.6, 27.0], [6.7, 27.0], [6.8, 27.0], [6.9, 27.0], [7.0, 27.0], [7.1, 27.0], [7.2, 27.0], [7.3, 27.0], [7.4, 27.0], [7.5, 27.0], [7.6, 27.0], [7.7, 27.0], [7.8, 27.0], [7.9, 27.0], [8.0, 27.0], [8.1, 27.0], [8.2, 27.0], [8.3, 27.0], [8.4, 27.0], [8.5, 27.0], [8.6, 27.0], [8.7, 27.0], [8.8, 27.0], [8.9, 28.0], [9.0, 28.0], [9.1, 28.0], [9.2, 28.0], [9.3, 28.0], [9.4, 28.0], [9.5, 28.0], [9.6, 28.0], [9.7, 28.0], [9.8, 28.0], [9.9, 28.0], [10.0, 28.0], [10.1, 28.0], [10.2, 28.0], [10.3, 28.0], [10.4, 28.0], [10.5, 28.0], [10.6, 28.0], [10.7, 28.0], [10.8, 28.0], [10.9, 28.0], [11.0, 28.0], [11.1, 28.0], [11.2, 28.0], [11.3, 28.0], [11.4, 28.0], [11.5, 28.0], [11.6, 28.0], [11.7, 28.0], [11.8, 28.0], [11.9, 28.0], [12.0, 28.0], [12.1, 28.0], [12.2, 28.0], [12.3, 28.0], [12.4, 28.0], [12.5, 28.0], [12.6, 28.0], [12.7, 28.0], [12.8, 28.0], [12.9, 28.0], [13.0, 28.0], [13.1, 28.0], [13.2, 28.0], [13.3, 28.0], [13.4, 28.0], [13.5, 28.0], [13.6, 28.0], [13.7, 28.0], [13.8, 29.0], [13.9, 29.0], [14.0, 29.0], [14.1, 29.0], [14.2, 29.0], [14.3, 29.0], [14.4, 29.0], [14.5, 29.0], [14.6, 29.0], [14.7, 29.0], [14.8, 29.0], [14.9, 29.0], [15.0, 29.0], [15.1, 29.0], [15.2, 29.0], [15.3, 29.0], [15.4, 29.0], [15.5, 29.0], [15.6, 29.0], [15.7, 29.0], [15.8, 29.0], [15.9, 29.0], [16.0, 29.0], [16.1, 29.0], [16.2, 29.0], [16.3, 29.0], [16.4, 29.0], [16.5, 29.0], [16.6, 29.0], [16.7, 29.0], [16.8, 29.0], [16.9, 29.0], [17.0, 29.0], [17.1, 29.0], [17.2, 29.0], [17.3, 29.0], [17.4, 29.0], [17.5, 29.0], [17.6, 29.0], [17.7, 29.0], [17.8, 29.0], [17.9, 29.0], [18.0, 29.0], [18.1, 29.0], [18.2, 29.0], [18.3, 29.0], [18.4, 29.0], [18.5, 29.0], [18.6, 29.0], [18.7, 29.0], [18.8, 29.0], [18.9, 29.0], [19.0, 29.0], [19.1, 29.0], [19.2, 29.0], [19.3, 29.0], [19.4, 29.0], [19.5, 29.0], [19.6, 29.0], [19.7, 29.0], [19.8, 29.0], [19.9, 29.0], [20.0, 29.0], [20.1, 29.0], [20.2, 29.0], [20.3, 29.0], [20.4, 29.0], [20.5, 29.0], [20.6, 29.0], [20.7, 29.0], [20.8, 30.0], [20.9, 30.0], [21.0, 30.0], [21.1, 30.0], [21.2, 30.0], [21.3, 30.0], [21.4, 30.0], [21.5, 30.0], [21.6, 30.0], [21.7, 30.0], [21.8, 30.0], [21.9, 30.0], [22.0, 30.0], [22.1, 30.0], [22.2, 30.0], [22.3, 30.0], [22.4, 30.0], [22.5, 30.0], [22.6, 30.0], [22.7, 30.0], [22.8, 30.0], [22.9, 30.0], [23.0, 30.0], [23.1, 30.0], [23.2, 30.0], [23.3, 30.0], [23.4, 30.0], [23.5, 30.0], [23.6, 30.0], [23.7, 30.0], [23.8, 30.0], [23.9, 30.0], [24.0, 30.0], [24.1, 30.0], [24.2, 30.0], [24.3, 30.0], [24.4, 30.0], [24.5, 30.0], [24.6, 30.0], [24.7, 30.0], [24.8, 30.0], [24.9, 30.0], [25.0, 30.0], [25.1, 30.0], [25.2, 30.0], [25.3, 30.0], [25.4, 30.0], [25.5, 30.0], [25.6, 30.0], [25.7, 30.0], [25.8, 30.0], [25.9, 30.0], [26.0, 30.0], [26.1, 30.0], [26.2, 30.0], [26.3, 30.0], [26.4, 30.0], [26.5, 30.0], [26.6, 30.0], [26.7, 30.0], [26.8, 30.0], [26.9, 30.0], [27.0, 30.0], [27.1, 30.0], [27.2, 30.0], [27.3, 30.0], [27.4, 30.0], [27.5, 30.0], [27.6, 30.0], [27.7, 30.0], [27.8, 30.0], [27.9, 30.0], [28.0, 30.0], [28.1, 30.0], [28.2, 30.0], [28.3, 30.0], [28.4, 30.0], [28.5, 30.0], [28.6, 30.0], [28.7, 30.0], [28.8, 30.0], [28.9, 30.0], [29.0, 30.0], [29.1, 30.0], [29.2, 30.0], [29.3, 31.0], [29.4, 31.0], [29.5, 31.0], [29.6, 31.0], [29.7, 31.0], [29.8, 31.0], [29.9, 31.0], [30.0, 31.0], [30.1, 31.0], [30.2, 31.0], [30.3, 31.0], [30.4, 31.0], [30.5, 31.0], [30.6, 31.0], [30.7, 31.0], [30.8, 31.0], [30.9, 31.0], [31.0, 31.0], [31.1, 31.0], [31.2, 31.0], [31.3, 31.0], [31.4, 31.0], [31.5, 31.0], [31.6, 31.0], [31.7, 31.0], [31.8, 31.0], [31.9, 31.0], [32.0, 31.0], [32.1, 31.0], [32.2, 31.0], [32.3, 31.0], [32.4, 31.0], [32.5, 31.0], [32.6, 31.0], [32.7, 31.0], [32.8, 31.0], [32.9, 31.0], [33.0, 31.0], [33.1, 31.0], [33.2, 31.0], [33.3, 31.0], [33.4, 31.0], [33.5, 31.0], [33.6, 31.0], [33.7, 31.0], [33.8, 31.0], [33.9, 31.0], [34.0, 31.0], [34.1, 31.0], [34.2, 31.0], [34.3, 31.0], [34.4, 31.0], [34.5, 31.0], [34.6, 31.0], [34.7, 31.0], [34.8, 31.0], [34.9, 31.0], [35.0, 31.0], [35.1, 31.0], [35.2, 31.0], [35.3, 31.0], [35.4, 31.0], [35.5, 31.0], [35.6, 31.0], [35.7, 31.0], [35.8, 31.0], [35.9, 31.0], [36.0, 31.0], [36.1, 31.0], [36.2, 31.0], [36.3, 31.0], [36.4, 31.0], [36.5, 31.0], [36.6, 31.0], [36.7, 31.0], [36.8, 31.0], [36.9, 31.0], [37.0, 31.0], [37.1, 31.0], [37.2, 32.0], [37.3, 32.0], [37.4, 32.0], [37.5, 32.0], [37.6, 32.0], [37.7, 32.0], [37.8, 32.0], [37.9, 32.0], [38.0, 32.0], [38.1, 32.0], [38.2, 32.0], [38.3, 32.0], [38.4, 32.0], [38.5, 32.0], [38.6, 32.0], [38.7, 32.0], [38.8, 32.0], [38.9, 32.0], [39.0, 32.0], [39.1, 32.0], [39.2, 32.0], [39.3, 32.0], [39.4, 32.0], [39.5, 32.0], [39.6, 32.0], [39.7, 32.0], [39.8, 32.0], [39.9, 32.0], [40.0, 32.0], [40.1, 32.0], [40.2, 32.0], [40.3, 32.0], [40.4, 32.0], [40.5, 32.0], [40.6, 32.0], [40.7, 32.0], [40.8, 32.0], [40.9, 32.0], [41.0, 32.0], [41.1, 32.0], [41.2, 32.0], [41.3, 32.0], [41.4, 32.0], [41.5, 32.0], [41.6, 32.0], [41.7, 32.0], [41.8, 32.0], [41.9, 32.0], [42.0, 32.0], [42.1, 32.0], [42.2, 32.0], [42.3, 32.0], [42.4, 32.0], [42.5, 32.0], [42.6, 32.0], [42.7, 32.0], [42.8, 32.0], [42.9, 32.0], [43.0, 32.0], [43.1, 32.0], [43.2, 33.0], [43.3, 33.0], [43.4, 33.0], [43.5, 33.0], [43.6, 33.0], [43.7, 33.0], [43.8, 33.0], [43.9, 33.0], [44.0, 33.0], [44.1, 33.0], [44.2, 33.0], [44.3, 33.0], [44.4, 33.0], [44.5, 33.0], [44.6, 33.0], [44.7, 33.0], [44.8, 33.0], [44.9, 33.0], [45.0, 33.0], [45.1, 33.0], [45.2, 33.0], [45.3, 33.0], [45.4, 33.0], [45.5, 33.0], [45.6, 33.0], [45.7, 33.0], [45.8, 33.0], [45.9, 33.0], [46.0, 33.0], [46.1, 33.0], [46.2, 33.0], [46.3, 33.0], [46.4, 33.0], [46.5, 33.0], [46.6, 33.0], [46.7, 33.0], [46.8, 33.0], [46.9, 33.0], [47.0, 33.0], [47.1, 33.0], [47.2, 33.0], [47.3, 33.0], [47.4, 34.0], [47.5, 34.0], [47.6, 34.0], [47.7, 34.0], [47.8, 34.0], [47.9, 34.0], [48.0, 34.0], [48.1, 34.0], [48.2, 34.0], [48.3, 34.0], [48.4, 34.0], [48.5, 34.0], [48.6, 34.0], [48.7, 34.0], [48.8, 34.0], [48.9, 34.0], [49.0, 34.0], [49.1, 34.0], [49.2, 34.0], [49.3, 34.0], [49.4, 34.0], [49.5, 34.0], [49.6, 34.0], [49.7, 34.0], [49.8, 34.0], [49.9, 34.0], [50.0, 34.0], [50.1, 34.0], [50.2, 34.0], [50.3, 34.0], [50.4, 34.0], [50.5, 34.0], [50.6, 35.0], [50.7, 35.0], [50.8, 35.0], [50.9, 35.0], [51.0, 35.0], [51.1, 35.0], [51.2, 35.0], [51.3, 35.0], [51.4, 35.0], [51.5, 35.0], [51.6, 35.0], [51.7, 35.0], [51.8, 35.0], [51.9, 35.0], [52.0, 35.0], [52.1, 35.0], [52.2, 35.0], [52.3, 35.0], [52.4, 35.0], [52.5, 35.0], [52.6, 35.0], [52.7, 35.0], [52.8, 35.0], [52.9, 35.0], [53.0, 35.0], [53.1, 35.0], [53.2, 36.0], [53.3, 36.0], [53.4, 36.0], [53.5, 36.0], [53.6, 36.0], [53.7, 36.0], [53.8, 36.0], [53.9, 36.0], [54.0, 36.0], [54.1, 36.0], [54.2, 36.0], [54.3, 36.0], [54.4, 36.0], [54.5, 36.0], [54.6, 36.0], [54.7, 36.0], [54.8, 36.0], [54.9, 36.0], [55.0, 36.0], [55.1, 36.0], [55.2, 36.0], [55.3, 36.0], [55.4, 36.0], [55.5, 36.0], [55.6, 37.0], [55.7, 37.0], [55.8, 37.0], [55.9, 37.0], [56.0, 37.0], [56.1, 37.0], [56.2, 37.0], [56.3, 37.0], [56.4, 37.0], [56.5, 37.0], [56.6, 37.0], [56.7, 37.0], [56.8, 37.0], [56.9, 37.0], [57.0, 37.0], [57.1, 37.0], [57.2, 37.0], [57.3, 37.0], [57.4, 37.0], [57.5, 37.0], [57.6, 37.0], [57.7, 38.0], [57.8, 38.0], [57.9, 38.0], [58.0, 38.0], [58.1, 38.0], [58.2, 38.0], [58.3, 38.0], [58.4, 38.0], [58.5, 38.0], [58.6, 38.0], [58.7, 38.0], [58.8, 38.0], [58.9, 38.0], [59.0, 38.0], [59.1, 38.0], [59.2, 38.0], [59.3, 38.0], [59.4, 38.0], [59.5, 38.0], [59.6, 38.0], [59.7, 39.0], [59.8, 39.0], [59.9, 39.0], [60.0, 39.0], [60.1, 39.0], [60.2, 39.0], [60.3, 39.0], [60.4, 39.0], [60.5, 39.0], [60.6, 39.0], [60.7, 39.0], [60.8, 39.0], [60.9, 39.0], [61.0, 39.0], [61.1, 39.0], [61.2, 39.0], [61.3, 39.0], [61.4, 39.0], [61.5, 39.0], [61.6, 40.0], [61.7, 40.0], [61.8, 40.0], [61.9, 40.0], [62.0, 40.0], [62.1, 40.0], [62.2, 40.0], [62.3, 40.0], [62.4, 40.0], [62.5, 40.0], [62.6, 40.0], [62.7, 40.0], [62.8, 40.0], [62.9, 40.0], [63.0, 40.0], [63.1, 40.0], [63.2, 40.0], [63.3, 40.0], [63.4, 40.0], [63.5, 41.0], [63.6, 41.0], [63.7, 41.0], [63.8, 41.0], [63.9, 41.0], [64.0, 41.0], [64.1, 41.0], [64.2, 41.0], [64.3, 41.0], [64.4, 41.0], [64.5, 41.0], [64.6, 41.0], [64.7, 41.0], [64.8, 41.0], [64.9, 41.0], [65.0, 41.0], [65.1, 41.0], [65.2, 42.0], [65.3, 42.0], [65.4, 42.0], [65.5, 42.0], [65.6, 42.0], [65.7, 42.0], [65.8, 42.0], [65.9, 42.0], [66.0, 42.0], [66.1, 42.0], [66.2, 42.0], [66.3, 42.0], [66.4, 42.0], [66.5, 42.0], [66.6, 42.0], [66.7, 42.0], [66.8, 42.0], [66.9, 43.0], [67.0, 43.0], [67.1, 43.0], [67.2, 43.0], [67.3, 43.0], [67.4, 43.0], [67.5, 43.0], [67.6, 43.0], [67.7, 43.0], [67.8, 43.0], [67.9, 43.0], [68.0, 43.0], [68.1, 43.0], [68.2, 43.0], [68.3, 43.0], [68.4, 43.0], [68.5, 43.0], [68.6, 44.0], [68.7, 44.0], [68.8, 44.0], [68.9, 44.0], [69.0, 44.0], [69.1, 44.0], [69.2, 44.0], [69.3, 44.0], [69.4, 44.0], [69.5, 44.0], [69.6, 44.0], [69.7, 44.0], [69.8, 44.0], [69.9, 44.0], [70.0, 44.0], [70.1, 45.0], [70.2, 45.0], [70.3, 45.0], [70.4, 45.0], [70.5, 45.0], [70.6, 45.0], [70.7, 45.0], [70.8, 45.0], [70.9, 45.0], [71.0, 45.0], [71.1, 45.0], [71.2, 45.0], [71.3, 45.0], [71.4, 45.0], [71.5, 45.0], [71.6, 46.0], [71.7, 46.0], [71.8, 46.0], [71.9, 46.0], [72.0, 46.0], [72.1, 46.0], [72.2, 46.0], [72.3, 46.0], [72.4, 46.0], [72.5, 46.0], [72.6, 46.0], [72.7, 46.0], [72.8, 46.0], [72.9, 46.0], [73.0, 47.0], [73.1, 47.0], [73.2, 47.0], [73.3, 47.0], [73.4, 47.0], [73.5, 47.0], [73.6, 47.0], [73.7, 47.0], [73.8, 47.0], [73.9, 47.0], [74.0, 47.0], [74.1, 47.0], [74.2, 47.0], [74.3, 47.0], [74.4, 47.0], [74.5, 47.0], [74.6, 48.0], [74.7, 48.0], [74.8, 48.0], [74.9, 48.0], [75.0, 48.0], [75.1, 48.0], [75.2, 48.0], [75.3, 48.0], [75.4, 48.0], [75.5, 48.0], [75.6, 48.0], [75.7, 48.0], [75.8, 48.0], [75.9, 48.0], [76.0, 48.0], [76.1, 49.0], [76.2, 49.0], [76.3, 49.0], [76.4, 49.0], [76.5, 49.0], [76.6, 49.0], [76.7, 49.0], [76.8, 49.0], [76.9, 49.0], [77.0, 49.0], [77.1, 49.0], [77.2, 49.0], [77.3, 49.0], [77.4, 49.0], [77.5, 49.0], [77.6, 49.0], [77.7, 50.0], [77.8, 50.0], [77.9, 50.0], [78.0, 50.0], [78.1, 50.0], [78.2, 50.0], [78.3, 50.0], [78.4, 50.0], [78.5, 50.0], [78.6, 50.0], [78.7, 50.0], [78.8, 50.0], [78.9, 50.0], [79.0, 51.0], [79.1, 51.0], [79.2, 51.0], [79.3, 51.0], [79.4, 51.0], [79.5, 51.0], [79.6, 51.0], [79.7, 51.0], [79.8, 51.0], [79.9, 51.0], [80.0, 51.0], [80.1, 51.0], [80.2, 52.0], [80.3, 52.0], [80.4, 52.0], [80.5, 52.0], [80.6, 52.0], [80.7, 52.0], [80.8, 52.0], [80.9, 52.0], [81.0, 52.0], [81.1, 52.0], [81.2, 53.0], [81.3, 53.0], [81.4, 53.0], [81.5, 53.0], [81.6, 53.0], [81.7, 53.0], [81.8, 53.0], [81.9, 53.0], [82.0, 54.0], [82.1, 54.0], [82.2, 54.0], [82.3, 54.0], [82.4, 54.0], [82.5, 54.0], [82.6, 54.0], [82.7, 54.0], [82.8, 55.0], [82.9, 55.0], [83.0, 55.0], [83.1, 55.0], [83.2, 55.0], [83.3, 55.0], [83.4, 55.0], [83.5, 56.0], [83.6, 56.0], [83.7, 56.0], [83.8, 56.0], [83.9, 56.0], [84.0, 56.0], [84.1, 56.0], [84.2, 57.0], [84.3, 57.0], [84.4, 57.0], [84.5, 57.0], [84.6, 57.0], [84.7, 57.0], [84.8, 58.0], [84.9, 58.0], [85.0, 58.0], [85.1, 58.0], [85.2, 58.0], [85.3, 59.0], [85.4, 59.0], [85.5, 59.0], [85.6, 59.0], [85.7, 59.0], [85.8, 60.0], [85.9, 60.0], [86.0, 60.0], [86.1, 60.0], [86.2, 60.0], [86.3, 61.0], [86.4, 61.0], [86.5, 61.0], [86.6, 61.0], [86.7, 61.0], [86.8, 62.0], [86.9, 62.0], [87.0, 62.0], [87.1, 62.0], [87.2, 63.0], [87.3, 63.0], [87.4, 63.0], [87.5, 63.0], [87.6, 64.0], [87.7, 64.0], [87.8, 64.0], [87.9, 64.0], [88.0, 65.0], [88.1, 65.0], [88.2, 65.0], [88.3, 66.0], [88.4, 66.0], [88.5, 67.0], [88.6, 67.0], [88.7, 67.0], [88.8, 68.0], [88.9, 68.0], [89.0, 69.0], [89.1, 69.0], [89.2, 69.0], [89.3, 70.0], [89.4, 70.0], [89.5, 71.0], [89.6, 72.0], [89.7, 72.0], [89.8, 73.0], [89.9, 73.0], [90.0, 74.0], [90.1, 74.0], [90.2, 75.0], [90.3, 75.0], [90.4, 76.0], [90.5, 76.0], [90.6, 77.0], [90.7, 77.0], [90.8, 78.0], [90.9, 78.0], [91.0, 79.0], [91.1, 80.0], [91.2, 80.0], [91.3, 81.0], [91.4, 81.0], [91.5, 82.0], [91.6, 83.0], [91.7, 83.0], [91.8, 84.0], [91.9, 84.0], [92.0, 85.0], [92.1, 86.0], [92.2, 87.0], [92.3, 88.0], [92.4, 89.0], [92.5, 90.0], [92.6, 91.0], [92.7, 92.0], [92.8, 93.0], [92.9, 94.0], [93.0, 95.0], [93.1, 95.0], [93.2, 97.0], [93.3, 97.0], [93.4, 98.0], [93.5, 99.0], [93.6, 100.0], [93.7, 101.0], [93.8, 102.0], [93.9, 103.0], [94.0, 104.0], [94.1, 106.0], [94.2, 107.0], [94.3, 108.0], [94.4, 109.0], [94.5, 110.0], [94.6, 111.0], [94.7, 111.0], [94.8, 112.0], [94.9, 113.0], [95.0, 114.0], [95.1, 114.0], [95.2, 115.0], [95.3, 116.0], [95.4, 117.0], [95.5, 118.0], [95.6, 118.0], [95.7, 119.0], [95.8, 120.0], [95.9, 121.0], [96.0, 123.0], [96.1, 124.0], [96.2, 125.0], [96.3, 128.0], [96.4, 130.0], [96.5, 133.0], [96.6, 135.0], [96.7, 137.0], [96.8, 138.0], [96.9, 140.0], [97.0, 141.0], [97.1, 143.0], [97.2, 145.0], [97.3, 147.0], [97.4, 148.0], [97.5, 149.0], [97.6, 151.0], [97.7, 152.0], [97.8, 154.0], [97.9, 155.0], [98.0, 157.0], [98.1, 159.0], [98.2, 161.0], [98.3, 166.0], [98.4, 170.0], [98.5, 174.0], [98.6, 180.0], [98.7, 185.0], [98.8, 194.0], [98.9, 201.0], [99.0, 212.0], [99.1, 228.0], [99.2, 245.0], [99.3, 257.0], [99.4, 266.0], [99.5, 275.0], [99.6, 314.0], [99.7, 385.0], [99.8, 507.0], [99.9, 915.0], [100.0, 8052.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 150100.0, "series": [{"data": [[0.0, 150100.0], [600.0, 39.0], [700.0, 54.0], [800.0, 6.0], [900.0, 57.0], [1000.0, 21.0], [1100.0, 7.0], [1200.0, 14.0], [1500.0, 1.0], [100.0, 8475.0], [2200.0, 1.0], [2300.0, 1.0], [200.0, 1168.0], [3400.0, 33.0], [3500.0, 2.0], [3800.0, 7.0], [300.0, 265.0], [5000.0, 1.0], [5300.0, 1.0], [5600.0, 35.0], [5800.0, 8.0], [5900.0, 1.0], [400.0, 67.0], [6400.0, 1.0], [6800.0, 1.0], [7300.0, 1.0], [500.0, 32.0], [8000.0, 1.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 8000.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 160400.0, "minX": 3.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 160400.0, "series": [{"data": [], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [[3.0, 160400.0]], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 3.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 30.35616254036608, "minX": 1.77360876E12, "maxY": 50.0, "series": [{"data": [[1.77360876E12, 30.35616254036608], [1.77360894E12, 49.95354534746757], [1.77360888E12, 50.0], [1.77360882E12, 50.0]], "isOverall": false, "label": "Concurrent Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360894E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 7.566308243727599, "minX": 1.0, "maxY": 484.4320987654322, "series": [{"data": [[2.0, 7.9545454545454515], [32.0, 76.24705882352937], [33.0, 107.46031746031748], [34.0, 76.71428571428571], [35.0, 81.15625], [36.0, 290.0425531914894], [37.0, 216.72950819672124], [38.0, 82.44052863436126], [39.0, 440.0769230769231], [40.0, 484.4320987654322], [41.0, 256.6500000000001], [42.0, 308.79999999999984], [46.0, 34.53846153846153], [3.0, 11.108843537414966], [50.0, 49.26756946375003], [4.0, 7.566308243727599], [5.0, 8.00307692307692], [6.0, 15.357466063348424], [7.0, 10.280991735537187], [8.0, 18.239999999999995], [9.0, 14.752089136490252], [10.0, 15.142857142857142], [11.0, 23.833962264150948], [12.0, 17.46891191709842], [13.0, 19.887362637362653], [14.0, 23.124645892351264], [15.0, 21.21666666666667], [1.0, 8.743589743589746], [16.0, 28.466165413533822], [17.0, 36.935361216730016], [18.0, 26.440721649484516], [19.0, 44.65306122448979], [20.0, 36.326018808777434], [21.0, 39.451923076923094], [22.0, 102.92982456140352], [23.0, 72.35922330097091], [24.0, 52.60648148148148], [25.0, 98.854748603352], [26.0, 48.12140575079871], [27.0, 73.93401015228426], [28.0, 124.05084745762716], [29.0, 340.53333333333336], [30.0, 110.03333333333332], [31.0, 116.46913580246911]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}, {"data": [[48.173491271821135, 49.59812344139632]], "isOverall": false, "label": "POST /api/v1/beta/translate-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 50.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 54344.683333333334, "minX": 1.77360876E12, "maxY": 564885.7666666667, "series": [{"data": [[1.77360876E12, 54344.683333333334], [1.77360894E12, 67566.25], [1.77360888E12, 220166.03333333333], [1.77360882E12, 186890.65]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.77360876E12, 124249.38333333333], [1.77360894E12, 177936.25], [1.77360888E12, 564885.7666666667], [1.77360882E12, 477254.7833333333]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360894E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 39.291213191990714, "minX": 1.77360876E12, "maxY": 90.3816603875138, "series": [{"data": [[1.77360876E12, 90.3816603875138], [1.77360894E12, 39.291213191990714], [1.77360888E12, 42.73641328544656], [1.77360882E12, 50.91403326951091]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360894E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 39.287161366313335, "minX": 1.77360876E12, "maxY": 90.2310279870827, "series": [{"data": [[1.77360876E12, 90.2310279870827], [1.77360894E12, 39.287161366313335], [1.77360888E12, 42.732881184886494], [1.77360882E12, 50.91020393823864]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360894E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.0, "minX": 1.77360876E12, "maxY": 0.010562432723358425, "series": [{"data": [[1.77360876E12, 0.010562432723358425], [1.77360894E12, 0.0], [1.77360888E12, 0.001083375382149535], [1.77360882E12, 0.0011769045653357668]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360894E12, "title": "Connect Time Over Time"}},
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
    data: {"result": {"minY": 6.0, "minX": 2.0, "maxY": 3998.5, "series": [{"data": [[2.0, 3998.5], [16.0, 9.0], [36.0, 351.0], [46.0, 3479.5], [78.0, 265.0], [85.0, 296.5], [120.0, 239.0], [124.0, 109.0], [164.0, 393.0], [173.0, 96.0], [176.0, 6.0], [200.0, 207.5], [247.0, 60.0], [265.0, 137.0], [281.0, 88.0], [284.0, 47.0], [299.0, 58.0], [348.0, 45.0], [350.0, 120.0], [376.0, 76.0], [407.0, 75.0], [427.0, 8.0], [430.0, 114.0], [440.0, 7.0], [432.0, 53.0], [482.0, 13.0], [511.0, 28.0], [500.0, 86.0], [519.0, 13.0], [527.0, 27.0], [525.0, 37.0], [531.0, 79.0], [558.0, 22.0], [550.0, 60.0], [595.0, 16.0], [603.0, 62.0], [600.0, 57.0], [615.0, 14.0], [611.0, 56.0], [633.0, 46.0], [660.0, 74.0], [650.0, 54.0], [654.0, 56.0], [661.0, 30.0], [700.0, 58.0], [689.0, 59.0], [695.0, 63.0], [723.0, 54.0], [715.0, 59.0], [705.0, 53.0], [712.0, 61.0], [739.0, 47.0], [750.0, 50.0], [776.0, 44.0], [777.0, 51.0], [799.0, 43.0], [773.0, 37.0], [800.0, 49.0], [825.0, 46.0], [804.0, 52.0], [821.0, 43.0], [856.0, 40.0], [850.0, 48.0], [855.0, 44.0], [891.0, 42.0], [876.0, 44.0], [900.0, 49.0], [920.0, 43.0], [951.0, 48.0], [930.0, 47.0], [952.0, 45.5], [954.0, 50.0], [958.0, 39.0], [978.0, 35.0], [1015.0, 34.0], [1000.0, 39.0], [1009.0, 34.0], [1046.0, 35.0], [1059.0, 43.0], [1086.0, 32.0], [1027.0, 42.0], [1084.0, 38.0], [1051.0, 32.0], [1067.0, 36.0], [1139.0, 42.0], [1115.0, 37.0], [1133.0, 35.0], [1150.0, 39.0], [1138.0, 30.0], [1106.0, 35.0], [1127.0, 31.0], [1200.0, 33.0], [1179.0, 37.0], [1154.0, 32.0], [1174.0, 30.0], [1207.0, 35.0], [1214.0, 37.0], [1188.0, 33.0], [1165.0, 30.0], [1190.0, 30.0], [1198.0, 32.0], [1273.0, 31.0], [1250.0, 34.0], [1226.0, 32.0], [1300.0, 31.0], [1341.0, 30.0], [1324.0, 31.0], [1327.0, 31.0], [1306.0, 33.0], [1320.0, 31.0], [1304.0, 32.0], [1307.0, 31.0], [1356.0, 33.5], [1368.0, 34.0], [1382.0, 33.0], [1376.0, 30.0], [1380.0, 30.0], [1360.0, 31.0], [1405.0, 30.0], [1403.0, 31.0], [1358.0, 31.0], [1365.0, 31.0], [1366.0, 31.0], [1375.0, 30.0], [1383.0, 31.0], [1408.0, 31.0], [1462.0, 31.0], [1458.0, 30.0], [1427.0, 30.0], [1412.0, 30.0], [1530.0, 30.0], [1532.0, 30.0], [1472.0, 31.0], [1500.0, 31.0], [1509.0, 30.0], [1505.0, 31.0], [1473.0, 31.0], [1510.0, 30.0], [1504.0, 30.0], [1568.0, 30.0], [1548.0, 31.0], [1550.0, 30.0], [1570.0, 30.0], [1562.0, 30.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 1570.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 6.0, "minX": 2.0, "maxY": 3479.5, "series": [{"data": [[2.0, 3201.0], [16.0, 9.0], [36.0, 351.0], [46.0, 3479.5], [78.0, 265.0], [85.0, 296.5], [120.0, 239.0], [124.0, 109.0], [164.0, 393.0], [173.0, 96.0], [176.0, 6.0], [200.0, 207.5], [247.0, 60.0], [265.0, 137.0], [281.0, 88.0], [284.0, 47.0], [299.0, 58.0], [348.0, 45.0], [350.0, 120.0], [376.0, 76.0], [407.0, 75.0], [427.0, 8.0], [430.0, 114.0], [440.0, 7.0], [432.0, 53.0], [482.0, 13.0], [511.0, 28.0], [500.0, 86.0], [519.0, 13.0], [527.0, 27.0], [525.0, 37.0], [531.0, 79.0], [558.0, 22.0], [550.0, 60.0], [595.0, 16.0], [603.0, 62.0], [600.0, 57.0], [615.0, 14.0], [611.0, 56.0], [633.0, 46.0], [660.0, 74.0], [650.0, 54.0], [654.0, 56.0], [661.0, 30.0], [700.0, 58.0], [689.0, 59.0], [695.0, 63.0], [723.0, 54.0], [715.0, 59.0], [705.0, 53.0], [712.0, 61.0], [739.0, 47.0], [750.0, 50.0], [776.0, 44.0], [777.0, 51.0], [799.0, 43.0], [773.0, 37.0], [800.0, 49.0], [825.0, 46.0], [804.0, 52.0], [821.0, 43.0], [856.0, 40.0], [850.0, 48.0], [855.0, 44.0], [891.0, 42.0], [876.0, 44.0], [900.0, 49.0], [920.0, 43.0], [951.0, 48.0], [930.0, 47.0], [952.0, 45.5], [954.0, 50.0], [958.0, 39.0], [978.0, 35.0], [1015.0, 34.0], [1000.0, 39.0], [1009.0, 34.0], [1046.0, 35.0], [1059.0, 43.0], [1086.0, 32.0], [1027.0, 42.0], [1084.0, 38.0], [1051.0, 32.0], [1067.0, 36.0], [1139.0, 42.0], [1115.0, 37.0], [1133.0, 35.0], [1150.0, 39.0], [1138.0, 30.0], [1106.0, 35.0], [1127.0, 31.0], [1200.0, 33.0], [1179.0, 37.0], [1154.0, 32.0], [1174.0, 30.0], [1207.0, 35.0], [1214.0, 37.0], [1188.0, 33.0], [1165.0, 30.0], [1190.0, 30.0], [1198.0, 32.0], [1273.0, 31.0], [1250.0, 34.0], [1226.0, 32.0], [1300.0, 31.0], [1341.0, 30.0], [1324.0, 31.0], [1327.0, 31.0], [1306.0, 33.0], [1320.0, 31.0], [1304.0, 32.0], [1307.0, 31.0], [1356.0, 33.5], [1368.0, 34.0], [1382.0, 33.0], [1376.0, 30.0], [1380.0, 30.0], [1360.0, 31.0], [1405.0, 30.0], [1403.0, 31.0], [1358.0, 31.0], [1365.0, 31.0], [1366.0, 31.0], [1375.0, 30.0], [1383.0, 31.0], [1408.0, 31.0], [1462.0, 31.0], [1458.0, 30.0], [1427.0, 30.0], [1412.0, 30.0], [1530.0, 30.0], [1532.0, 30.0], [1472.0, 31.0], [1500.0, 31.0], [1509.0, 30.0], [1505.0, 31.0], [1473.0, 31.0], [1510.0, 30.0], [1504.0, 30.0], [1568.0, 30.0], [1548.0, 31.0], [1550.0, 30.0], [1570.0, 30.0], [1562.0, 30.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 1570.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 248.56666666666666, "minX": 1.77360876E12, "maxY": 1123.0333333333333, "series": [{"data": [[1.77360876E12, 248.56666666666666], [1.77360894E12, 352.9166666666667], [1.77360888E12, 1123.0333333333333], [1.77360882E12, 948.8166666666667]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360894E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 0.7166666666666667, "minX": 1.77360876E12, "maxY": 956.3666666666667, "series": [{"data": [[1.77360876E12, 166.66666666666666], [1.77360888E12, 166.66666666666666], [1.77360882E12, 166.66666666666666]], "isOverall": false, "label": "422", "isController": false}, {"data": [[1.77360876E12, 0.7166666666666667]], "isOverall": false, "label": "Non HTTP response code: org.apache.http.NoHttpResponseException", "isController": false}, {"data": [[1.77360876E12, 80.35], [1.77360894E12, 353.75], [1.77360888E12, 956.3666666666667], [1.77360882E12, 782.15]], "isOverall": false, "label": "429", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360894E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 247.73333333333332, "minX": 1.77360876E12, "maxY": 1123.0333333333333, "series": [{"data": [[1.77360876E12, 247.73333333333332], [1.77360894E12, 353.75], [1.77360888E12, 1123.0333333333333], [1.77360882E12, 948.8166666666667]], "isOverall": false, "label": "POST /api/v1/beta/translate-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360894E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 247.73333333333332, "minX": 1.77360876E12, "maxY": 1123.0333333333333, "series": [{"data": [], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [[1.77360876E12, 247.73333333333332], [1.77360894E12, 353.75], [1.77360888E12, 1123.0333333333333], [1.77360882E12, 948.8166666666667]], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360894E12, "title": "Total Transactions Per Second"}},
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

