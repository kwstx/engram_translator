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
        data: {"result": {"minY": 8.0, "minX": 0.0, "maxY": 345.0, "series": [{"data": [[0.0, 8.0], [0.1, 9.0], [0.2, 11.0], [0.3, 12.0], [0.4, 12.0], [0.5, 13.0], [0.6, 13.0], [0.7, 13.0], [0.8, 13.0], [0.9, 13.0], [1.0, 13.0], [1.1, 14.0], [1.2, 14.0], [1.3, 14.0], [1.4, 14.0], [1.5, 15.0], [1.6, 15.0], [1.7, 15.0], [1.8, 15.0], [1.9, 16.0], [2.0, 16.0], [2.1, 16.0], [2.2, 16.0], [2.3, 16.0], [2.4, 17.0], [2.5, 17.0], [2.6, 17.0], [2.7, 17.0], [2.8, 17.0], [2.9, 18.0], [3.0, 18.0], [3.1, 18.0], [3.2, 18.0], [3.3, 18.0], [3.4, 18.0], [3.5, 19.0], [3.6, 19.0], [3.7, 19.0], [3.8, 20.0], [3.9, 20.0], [4.0, 21.0], [4.1, 21.0], [4.2, 21.0], [4.3, 21.0], [4.4, 22.0], [4.5, 22.0], [4.6, 22.0], [4.7, 23.0], [4.8, 23.0], [4.9, 23.0], [5.0, 23.0], [5.1, 23.0], [5.2, 23.0], [5.3, 23.0], [5.4, 24.0], [5.5, 24.0], [5.6, 24.0], [5.7, 24.0], [5.8, 24.0], [5.9, 24.0], [6.0, 24.0], [6.1, 24.0], [6.2, 24.0], [6.3, 24.0], [6.4, 24.0], [6.5, 24.0], [6.6, 24.0], [6.7, 24.0], [6.8, 25.0], [6.9, 25.0], [7.0, 25.0], [7.1, 25.0], [7.2, 25.0], [7.3, 25.0], [7.4, 25.0], [7.5, 25.0], [7.6, 25.0], [7.7, 25.0], [7.8, 25.0], [7.9, 25.0], [8.0, 25.0], [8.1, 25.0], [8.2, 25.0], [8.3, 25.0], [8.4, 26.0], [8.5, 26.0], [8.6, 26.0], [8.7, 26.0], [8.8, 26.0], [8.9, 26.0], [9.0, 26.0], [9.1, 26.0], [9.2, 26.0], [9.3, 26.0], [9.4, 26.0], [9.5, 27.0], [9.6, 27.0], [9.7, 27.0], [9.8, 27.0], [9.9, 27.0], [10.0, 27.0], [10.1, 27.0], [10.2, 27.0], [10.3, 27.0], [10.4, 27.0], [10.5, 27.0], [10.6, 27.0], [10.7, 28.0], [10.8, 28.0], [10.9, 28.0], [11.0, 28.0], [11.1, 28.0], [11.2, 28.0], [11.3, 28.0], [11.4, 28.0], [11.5, 28.0], [11.6, 28.0], [11.7, 28.0], [11.8, 28.0], [11.9, 28.0], [12.0, 28.0], [12.1, 29.0], [12.2, 29.0], [12.3, 29.0], [12.4, 29.0], [12.5, 29.0], [12.6, 29.0], [12.7, 29.0], [12.8, 29.0], [12.9, 29.0], [13.0, 29.0], [13.1, 29.0], [13.2, 29.0], [13.3, 29.0], [13.4, 29.0], [13.5, 29.0], [13.6, 29.0], [13.7, 29.0], [13.8, 30.0], [13.9, 30.0], [14.0, 30.0], [14.1, 30.0], [14.2, 30.0], [14.3, 30.0], [14.4, 30.0], [14.5, 30.0], [14.6, 30.0], [14.7, 30.0], [14.8, 30.0], [14.9, 30.0], [15.0, 30.0], [15.1, 30.0], [15.2, 30.0], [15.3, 30.0], [15.4, 30.0], [15.5, 30.0], [15.6, 30.0], [15.7, 30.0], [15.8, 30.0], [15.9, 31.0], [16.0, 31.0], [16.1, 31.0], [16.2, 31.0], [16.3, 31.0], [16.4, 31.0], [16.5, 31.0], [16.6, 31.0], [16.7, 31.0], [16.8, 31.0], [16.9, 31.0], [17.0, 31.0], [17.1, 31.0], [17.2, 31.0], [17.3, 31.0], [17.4, 31.0], [17.5, 31.0], [17.6, 31.0], [17.7, 31.0], [17.8, 31.0], [17.9, 31.0], [18.0, 31.0], [18.1, 31.0], [18.2, 32.0], [18.3, 32.0], [18.4, 32.0], [18.5, 32.0], [18.6, 32.0], [18.7, 32.0], [18.8, 32.0], [18.9, 32.0], [19.0, 32.0], [19.1, 32.0], [19.2, 32.0], [19.3, 32.0], [19.4, 32.0], [19.5, 32.0], [19.6, 32.0], [19.7, 32.0], [19.8, 32.0], [19.9, 32.0], [20.0, 32.0], [20.1, 32.0], [20.2, 32.0], [20.3, 32.0], [20.4, 32.0], [20.5, 32.0], [20.6, 32.0], [20.7, 32.0], [20.8, 32.0], [20.9, 32.0], [21.0, 32.0], [21.1, 32.0], [21.2, 33.0], [21.3, 33.0], [21.4, 33.0], [21.5, 33.0], [21.6, 33.0], [21.7, 33.0], [21.8, 33.0], [21.9, 33.0], [22.0, 33.0], [22.1, 33.0], [22.2, 33.0], [22.3, 33.0], [22.4, 33.0], [22.5, 33.0], [22.6, 33.0], [22.7, 33.0], [22.8, 33.0], [22.9, 33.0], [23.0, 33.0], [23.1, 33.0], [23.2, 33.0], [23.3, 33.0], [23.4, 33.0], [23.5, 33.0], [23.6, 33.0], [23.7, 33.0], [23.8, 33.0], [23.9, 33.0], [24.0, 33.0], [24.1, 33.0], [24.2, 33.0], [24.3, 34.0], [24.4, 34.0], [24.5, 34.0], [24.6, 34.0], [24.7, 34.0], [24.8, 34.0], [24.9, 34.0], [25.0, 34.0], [25.1, 34.0], [25.2, 34.0], [25.3, 34.0], [25.4, 34.0], [25.5, 34.0], [25.6, 34.0], [25.7, 34.0], [25.8, 34.0], [25.9, 34.0], [26.0, 34.0], [26.1, 34.0], [26.2, 34.0], [26.3, 34.0], [26.4, 34.0], [26.5, 34.0], [26.6, 34.0], [26.7, 34.0], [26.8, 34.0], [26.9, 34.0], [27.0, 34.0], [27.1, 34.0], [27.2, 34.0], [27.3, 34.0], [27.4, 34.0], [27.5, 34.0], [27.6, 34.0], [27.7, 34.0], [27.8, 34.0], [27.9, 34.0], [28.0, 35.0], [28.1, 35.0], [28.2, 35.0], [28.3, 35.0], [28.4, 35.0], [28.5, 35.0], [28.6, 35.0], [28.7, 35.0], [28.8, 35.0], [28.9, 35.0], [29.0, 35.0], [29.1, 35.0], [29.2, 35.0], [29.3, 35.0], [29.4, 35.0], [29.5, 35.0], [29.6, 35.0], [29.7, 35.0], [29.8, 35.0], [29.9, 35.0], [30.0, 35.0], [30.1, 35.0], [30.2, 35.0], [30.3, 35.0], [30.4, 35.0], [30.5, 35.0], [30.6, 35.0], [30.7, 35.0], [30.8, 35.0], [30.9, 35.0], [31.0, 35.0], [31.1, 35.0], [31.2, 35.0], [31.3, 35.0], [31.4, 35.0], [31.5, 35.0], [31.6, 35.0], [31.7, 35.0], [31.8, 36.0], [31.9, 36.0], [32.0, 36.0], [32.1, 36.0], [32.2, 36.0], [32.3, 36.0], [32.4, 36.0], [32.5, 36.0], [32.6, 36.0], [32.7, 36.0], [32.8, 36.0], [32.9, 36.0], [33.0, 36.0], [33.1, 36.0], [33.2, 36.0], [33.3, 36.0], [33.4, 36.0], [33.5, 36.0], [33.6, 36.0], [33.7, 36.0], [33.8, 36.0], [33.9, 36.0], [34.0, 36.0], [34.1, 36.0], [34.2, 36.0], [34.3, 36.0], [34.4, 36.0], [34.5, 36.0], [34.6, 36.0], [34.7, 36.0], [34.8, 36.0], [34.9, 36.0], [35.0, 36.0], [35.1, 36.0], [35.2, 36.0], [35.3, 36.0], [35.4, 36.0], [35.5, 36.0], [35.6, 36.0], [35.7, 36.0], [35.8, 36.0], [35.9, 36.0], [36.0, 36.0], [36.1, 36.0], [36.2, 37.0], [36.3, 37.0], [36.4, 37.0], [36.5, 37.0], [36.6, 37.0], [36.7, 37.0], [36.8, 37.0], [36.9, 37.0], [37.0, 37.0], [37.1, 37.0], [37.2, 37.0], [37.3, 37.0], [37.4, 37.0], [37.5, 37.0], [37.6, 37.0], [37.7, 37.0], [37.8, 37.0], [37.9, 37.0], [38.0, 37.0], [38.1, 37.0], [38.2, 37.0], [38.3, 37.0], [38.4, 37.0], [38.5, 37.0], [38.6, 37.0], [38.7, 37.0], [38.8, 37.0], [38.9, 37.0], [39.0, 37.0], [39.1, 37.0], [39.2, 37.0], [39.3, 37.0], [39.4, 37.0], [39.5, 37.0], [39.6, 37.0], [39.7, 37.0], [39.8, 37.0], [39.9, 37.0], [40.0, 37.0], [40.1, 37.0], [40.2, 37.0], [40.3, 37.0], [40.4, 37.0], [40.5, 37.0], [40.6, 37.0], [40.7, 37.0], [40.8, 38.0], [40.9, 38.0], [41.0, 38.0], [41.1, 38.0], [41.2, 38.0], [41.3, 38.0], [41.4, 38.0], [41.5, 38.0], [41.6, 38.0], [41.7, 38.0], [41.8, 38.0], [41.9, 38.0], [42.0, 38.0], [42.1, 38.0], [42.2, 38.0], [42.3, 38.0], [42.4, 38.0], [42.5, 38.0], [42.6, 38.0], [42.7, 38.0], [42.8, 38.0], [42.9, 38.0], [43.0, 38.0], [43.1, 38.0], [43.2, 38.0], [43.3, 38.0], [43.4, 38.0], [43.5, 38.0], [43.6, 38.0], [43.7, 38.0], [43.8, 38.0], [43.9, 38.0], [44.0, 38.0], [44.1, 38.0], [44.2, 38.0], [44.3, 38.0], [44.4, 38.0], [44.5, 38.0], [44.6, 38.0], [44.7, 38.0], [44.8, 38.0], [44.9, 38.0], [45.0, 38.0], [45.1, 38.0], [45.2, 38.0], [45.3, 38.0], [45.4, 38.0], [45.5, 38.0], [45.6, 38.0], [45.7, 39.0], [45.8, 39.0], [45.9, 39.0], [46.0, 39.0], [46.1, 39.0], [46.2, 39.0], [46.3, 39.0], [46.4, 39.0], [46.5, 39.0], [46.6, 39.0], [46.7, 39.0], [46.8, 39.0], [46.9, 39.0], [47.0, 39.0], [47.1, 39.0], [47.2, 39.0], [47.3, 39.0], [47.4, 39.0], [47.5, 39.0], [47.6, 39.0], [47.7, 39.0], [47.8, 39.0], [47.9, 39.0], [48.0, 39.0], [48.1, 39.0], [48.2, 39.0], [48.3, 39.0], [48.4, 39.0], [48.5, 39.0], [48.6, 39.0], [48.7, 39.0], [48.8, 39.0], [48.9, 39.0], [49.0, 39.0], [49.1, 39.0], [49.2, 39.0], [49.3, 39.0], [49.4, 39.0], [49.5, 39.0], [49.6, 39.0], [49.7, 39.0], [49.8, 40.0], [49.9, 40.0], [50.0, 40.0], [50.1, 40.0], [50.2, 40.0], [50.3, 40.0], [50.4, 40.0], [50.5, 40.0], [50.6, 40.0], [50.7, 40.0], [50.8, 40.0], [50.9, 40.0], [51.0, 40.0], [51.1, 40.0], [51.2, 40.0], [51.3, 40.0], [51.4, 40.0], [51.5, 40.0], [51.6, 40.0], [51.7, 40.0], [51.8, 40.0], [51.9, 40.0], [52.0, 40.0], [52.1, 40.0], [52.2, 40.0], [52.3, 40.0], [52.4, 40.0], [52.5, 40.0], [52.6, 40.0], [52.7, 40.0], [52.8, 40.0], [52.9, 40.0], [53.0, 40.0], [53.1, 40.0], [53.2, 40.0], [53.3, 40.0], [53.4, 40.0], [53.5, 40.0], [53.6, 40.0], [53.7, 41.0], [53.8, 41.0], [53.9, 41.0], [54.0, 41.0], [54.1, 41.0], [54.2, 41.0], [54.3, 41.0], [54.4, 41.0], [54.5, 41.0], [54.6, 41.0], [54.7, 41.0], [54.8, 41.0], [54.9, 41.0], [55.0, 41.0], [55.1, 41.0], [55.2, 41.0], [55.3, 41.0], [55.4, 41.0], [55.5, 41.0], [55.6, 41.0], [55.7, 41.0], [55.8, 41.0], [55.9, 41.0], [56.0, 41.0], [56.1, 41.0], [56.2, 41.0], [56.3, 41.0], [56.4, 41.0], [56.5, 41.0], [56.6, 41.0], [56.7, 41.0], [56.8, 41.0], [56.9, 41.0], [57.0, 41.0], [57.1, 41.0], [57.2, 41.0], [57.3, 41.0], [57.4, 42.0], [57.5, 42.0], [57.6, 42.0], [57.7, 42.0], [57.8, 42.0], [57.9, 42.0], [58.0, 42.0], [58.1, 42.0], [58.2, 42.0], [58.3, 42.0], [58.4, 42.0], [58.5, 42.0], [58.6, 42.0], [58.7, 42.0], [58.8, 42.0], [58.9, 42.0], [59.0, 42.0], [59.1, 42.0], [59.2, 42.0], [59.3, 42.0], [59.4, 42.0], [59.5, 42.0], [59.6, 42.0], [59.7, 42.0], [59.8, 42.0], [59.9, 42.0], [60.0, 42.0], [60.1, 42.0], [60.2, 42.0], [60.3, 42.0], [60.4, 42.0], [60.5, 42.0], [60.6, 42.0], [60.7, 42.0], [60.8, 42.0], [60.9, 42.0], [61.0, 42.0], [61.1, 42.0], [61.2, 42.0], [61.3, 43.0], [61.4, 43.0], [61.5, 43.0], [61.6, 43.0], [61.7, 43.0], [61.8, 43.0], [61.9, 43.0], [62.0, 43.0], [62.1, 43.0], [62.2, 43.0], [62.3, 43.0], [62.4, 43.0], [62.5, 43.0], [62.6, 43.0], [62.7, 43.0], [62.8, 43.0], [62.9, 43.0], [63.0, 43.0], [63.1, 43.0], [63.2, 43.0], [63.3, 43.0], [63.4, 43.0], [63.5, 43.0], [63.6, 43.0], [63.7, 43.0], [63.8, 43.0], [63.9, 44.0], [64.0, 44.0], [64.1, 44.0], [64.2, 44.0], [64.3, 44.0], [64.4, 44.0], [64.5, 44.0], [64.6, 44.0], [64.7, 44.0], [64.8, 44.0], [64.9, 44.0], [65.0, 44.0], [65.1, 44.0], [65.2, 44.0], [65.3, 44.0], [65.4, 44.0], [65.5, 44.0], [65.6, 44.0], [65.7, 44.0], [65.8, 44.0], [65.9, 44.0], [66.0, 44.0], [66.1, 44.0], [66.2, 44.0], [66.3, 44.0], [66.4, 44.0], [66.5, 44.0], [66.6, 45.0], [66.7, 45.0], [66.8, 45.0], [66.9, 45.0], [67.0, 45.0], [67.1, 45.0], [67.2, 45.0], [67.3, 45.0], [67.4, 45.0], [67.5, 45.0], [67.6, 45.0], [67.7, 45.0], [67.8, 45.0], [67.9, 45.0], [68.0, 45.0], [68.1, 45.0], [68.2, 45.0], [68.3, 45.0], [68.4, 45.0], [68.5, 45.0], [68.6, 45.0], [68.7, 45.0], [68.8, 45.0], [68.9, 46.0], [69.0, 46.0], [69.1, 46.0], [69.2, 46.0], [69.3, 46.0], [69.4, 46.0], [69.5, 46.0], [69.6, 46.0], [69.7, 46.0], [69.8, 46.0], [69.9, 46.0], [70.0, 46.0], [70.1, 46.0], [70.2, 46.0], [70.3, 46.0], [70.4, 46.0], [70.5, 46.0], [70.6, 46.0], [70.7, 46.0], [70.8, 46.0], [70.9, 46.0], [71.0, 46.0], [71.1, 47.0], [71.2, 47.0], [71.3, 47.0], [71.4, 47.0], [71.5, 47.0], [71.6, 47.0], [71.7, 47.0], [71.8, 47.0], [71.9, 47.0], [72.0, 47.0], [72.1, 47.0], [72.2, 47.0], [72.3, 47.0], [72.4, 47.0], [72.5, 47.0], [72.6, 47.0], [72.7, 47.0], [72.8, 47.0], [72.9, 48.0], [73.0, 48.0], [73.1, 48.0], [73.2, 48.0], [73.3, 48.0], [73.4, 48.0], [73.5, 48.0], [73.6, 48.0], [73.7, 48.0], [73.8, 48.0], [73.9, 48.0], [74.0, 48.0], [74.1, 48.0], [74.2, 48.0], [74.3, 48.0], [74.4, 48.0], [74.5, 48.0], [74.6, 48.0], [74.7, 48.0], [74.8, 48.0], [74.9, 48.0], [75.0, 48.0], [75.1, 49.0], [75.2, 49.0], [75.3, 49.0], [75.4, 49.0], [75.5, 49.0], [75.6, 49.0], [75.7, 49.0], [75.8, 49.0], [75.9, 49.0], [76.0, 49.0], [76.1, 49.0], [76.2, 49.0], [76.3, 49.0], [76.4, 49.0], [76.5, 49.0], [76.6, 49.0], [76.7, 49.0], [76.8, 49.0], [76.9, 49.0], [77.0, 49.0], [77.1, 49.0], [77.2, 50.0], [77.3, 50.0], [77.4, 50.0], [77.5, 50.0], [77.6, 50.0], [77.7, 50.0], [77.8, 50.0], [77.9, 50.0], [78.0, 50.0], [78.1, 50.0], [78.2, 50.0], [78.3, 50.0], [78.4, 50.0], [78.5, 50.0], [78.6, 51.0], [78.7, 51.0], [78.8, 51.0], [78.9, 51.0], [79.0, 51.0], [79.1, 51.0], [79.2, 51.0], [79.3, 51.0], [79.4, 51.0], [79.5, 51.0], [79.6, 51.0], [79.7, 51.0], [79.8, 51.0], [79.9, 51.0], [80.0, 51.0], [80.1, 51.0], [80.2, 52.0], [80.3, 52.0], [80.4, 52.0], [80.5, 52.0], [80.6, 52.0], [80.7, 52.0], [80.8, 52.0], [80.9, 52.0], [81.0, 53.0], [81.1, 53.0], [81.2, 53.0], [81.3, 53.0], [81.4, 53.0], [81.5, 53.0], [81.6, 53.0], [81.7, 53.0], [81.8, 53.0], [81.9, 53.0], [82.0, 54.0], [82.1, 54.0], [82.2, 54.0], [82.3, 54.0], [82.4, 54.0], [82.5, 54.0], [82.6, 54.0], [82.7, 54.0], [82.8, 54.0], [82.9, 54.0], [83.0, 54.0], [83.1, 55.0], [83.2, 55.0], [83.3, 55.0], [83.4, 55.0], [83.5, 55.0], [83.6, 55.0], [83.7, 55.0], [83.8, 55.0], [83.9, 55.0], [84.0, 56.0], [84.1, 56.0], [84.2, 56.0], [84.3, 56.0], [84.4, 56.0], [84.5, 56.0], [84.6, 56.0], [84.7, 57.0], [84.8, 57.0], [84.9, 57.0], [85.0, 57.0], [85.1, 58.0], [85.2, 58.0], [85.3, 58.0], [85.4, 58.0], [85.5, 59.0], [85.6, 59.0], [85.7, 59.0], [85.8, 59.0], [85.9, 59.0], [86.0, 59.0], [86.1, 59.0], [86.2, 59.0], [86.3, 60.0], [86.4, 60.0], [86.5, 60.0], [86.6, 60.0], [86.7, 61.0], [86.8, 61.0], [86.9, 61.0], [87.0, 61.0], [87.1, 61.0], [87.2, 61.0], [87.3, 61.0], [87.4, 61.0], [87.5, 61.0], [87.6, 62.0], [87.7, 62.0], [87.8, 62.0], [87.9, 62.0], [88.0, 62.0], [88.1, 62.0], [88.2, 62.0], [88.3, 62.0], [88.4, 63.0], [88.5, 63.0], [88.6, 63.0], [88.7, 63.0], [88.8, 63.0], [88.9, 64.0], [89.0, 64.0], [89.1, 64.0], [89.2, 64.0], [89.3, 65.0], [89.4, 65.0], [89.5, 65.0], [89.6, 66.0], [89.7, 66.0], [89.8, 66.0], [89.9, 66.0], [90.0, 67.0], [90.1, 67.0], [90.2, 67.0], [90.3, 68.0], [90.4, 70.0], [90.5, 70.0], [90.6, 70.0], [90.7, 70.0], [90.8, 70.0], [90.9, 71.0], [91.0, 71.0], [91.1, 71.0], [91.2, 71.0], [91.3, 72.0], [91.4, 72.0], [91.5, 72.0], [91.6, 72.0], [91.7, 73.0], [91.8, 73.0], [91.9, 74.0], [92.0, 74.0], [92.1, 75.0], [92.2, 75.0], [92.3, 76.0], [92.4, 77.0], [92.5, 77.0], [92.6, 78.0], [92.7, 78.0], [92.8, 79.0], [92.9, 79.0], [93.0, 79.0], [93.1, 80.0], [93.2, 80.0], [93.3, 81.0], [93.4, 81.0], [93.5, 81.0], [93.6, 81.0], [93.7, 82.0], [93.8, 82.0], [93.9, 82.0], [94.0, 83.0], [94.1, 84.0], [94.2, 84.0], [94.3, 85.0], [94.4, 86.0], [94.5, 86.0], [94.6, 88.0], [94.7, 89.0], [94.8, 90.0], [94.9, 90.0], [95.0, 93.0], [95.1, 96.0], [95.2, 97.0], [95.3, 98.0], [95.4, 99.0], [95.5, 101.0], [95.6, 102.0], [95.7, 104.0], [95.8, 105.0], [95.9, 107.0], [96.0, 108.0], [96.1, 112.0], [96.2, 112.0], [96.3, 113.0], [96.4, 114.0], [96.5, 116.0], [96.6, 116.0], [96.7, 117.0], [96.8, 117.0], [96.9, 117.0], [97.0, 117.0], [97.1, 118.0], [97.2, 119.0], [97.3, 122.0], [97.4, 125.0], [97.5, 126.0], [97.6, 128.0], [97.7, 129.0], [97.8, 129.0], [97.9, 130.0], [98.0, 131.0], [98.1, 132.0], [98.2, 132.0], [98.3, 132.0], [98.4, 133.0], [98.5, 134.0], [98.6, 134.0], [98.7, 137.0], [98.8, 157.0], [98.9, 159.0], [99.0, 200.0], [99.1, 202.0], [99.2, 216.0], [99.3, 216.0], [99.4, 219.0], [99.5, 290.0], [99.6, 291.0], [99.7, 295.0], [99.8, 341.0], [99.9, 344.0], [100.0, 345.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 10.0, "minX": 0.0, "maxY": 3598.0, "series": [{"data": [[0.0, 3598.0], [300.0, 10.0], [200.0, 28.0], [100.0, 134.0]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 300.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 3770.0, "minX": 3.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 3770.0, "series": [{"data": [], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [[3.0, 3770.0]], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 3.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 9.290185676392563, "minX": 1.77360966E12, "maxY": 9.290185676392563, "series": [{"data": [[1.77360966E12, 9.290185676392563]], "isOverall": false, "label": "Concurrent Users", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360966E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 17.22641509433963, "minX": 1.0, "maxY": 52.66666666666667, "series": [{"data": [[1.0, 52.66666666666667], [2.0, 17.22641509433963], [4.0, 30.593750000000004], [8.0, 40.57894736842105], [9.0, 44.00000000000001], [5.0, 32.07692307692308], [10.0, 48.96303377947735], [3.0, 17.637499999999996], [6.0, 33.41666666666667], [7.0, 44.26506024096385]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}, {"data": [[9.290185676392563, 46.418567639257255]], "isOverall": false, "label": "POST /api/v1/beta/translate-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 10.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 14137.5, "minX": 1.77360966E12, "maxY": 31605.166666666668, "series": [{"data": [[1.77360966E12, 14137.5]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.77360966E12, 31605.166666666668]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360966E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 46.418567639257255, "minX": 1.77360966E12, "maxY": 46.418567639257255, "series": [{"data": [[1.77360966E12, 46.418567639257255]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360966E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 46.375862068965525, "minX": 1.77360966E12, "maxY": 46.375862068965525, "series": [{"data": [[1.77360966E12, 46.375862068965525]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360966E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.05490716180371343, "minX": 1.77360966E12, "maxY": 0.05490716180371343, "series": [{"data": [[1.77360966E12, 0.05490716180371343]], "isOverall": false, "label": "POST /api/v1/beta/translate", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360966E12, "title": "Connect Time Over Time"}},
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
    data: {"result": {"minY": 16.0, "minX": 82.0, "maxY": 105.0, "series": [{"data": [[134.0, 18.0], [166.0, 59.5], [174.0, 35.0], [172.0, 39.0], [180.0, 43.5], [177.0, 51.0], [191.0, 42.0], [186.0, 45.0], [200.0, 43.0], [213.0, 46.0], [230.0, 42.0], [224.0, 38.0], [237.0, 40.0], [250.0, 39.0], [260.0, 35.0], [82.0, 16.0], [320.0, 31.0], [85.0, 105.0], [115.0, 46.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 320.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 16.0, "minX": 82.0, "maxY": 105.0, "series": [{"data": [[134.0, 18.0], [166.0, 59.5], [174.0, 35.0], [172.0, 39.0], [180.0, 43.5], [177.0, 51.0], [191.0, 42.0], [186.0, 45.0], [200.0, 43.0], [213.0, 46.0], [230.0, 42.0], [224.0, 38.0], [237.0, 40.0], [250.0, 39.0], [260.0, 35.0], [82.0, 16.0], [320.0, 31.0], [85.0, 105.0], [115.0, 46.0]], "isOverall": false, "label": "Failures", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 320.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 62.833333333333336, "minX": 1.77360966E12, "maxY": 62.833333333333336, "series": [{"data": [[1.77360966E12, 62.833333333333336]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360966E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 62.833333333333336, "minX": 1.77360966E12, "maxY": 62.833333333333336, "series": [{"data": [[1.77360966E12, 62.833333333333336]], "isOverall": false, "label": "422", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.77360966E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 62.833333333333336, "minX": 1.77360966E12, "maxY": 62.833333333333336, "series": [{"data": [[1.77360966E12, 62.833333333333336]], "isOverall": false, "label": "POST /api/v1/beta/translate-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360966E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 62.833333333333336, "minX": 1.77360966E12, "maxY": 62.833333333333336, "series": [{"data": [], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [[1.77360966E12, 62.833333333333336]], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.77360966E12, "title": "Total Transactions Per Second"}},
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

