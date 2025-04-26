function getBestTrade() {
  const now = new Date();
  const hours = now.getHours();
  const minutes = now.getMinutes();

  // Market hours: 9:15 AM to 3:30 PM
  const isMarketTime = (hours === 9 && minutes >= 15) || (hours > 9 && hours < 15) || (hours === 15 && minutes <= 30);

  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sheet1");
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Logs");

  // âœ… Show last refreshed time
  sheet.getRange("J1").setValue("Last Checked");
  sheet.getRange("J2").setValue(now);

  if (!isMarketTime) {
    Logger.log("Outside market hours. Skipping API call.");
    return;
  }

  const url = "https://nse-signal-fresh.onrender.com/besttrade";
  const response = UrlFetchApp.fetch(url);
  const json = JSON.parse(response.getContentText());

  if (json.symbol) {
    // âœ… Display current signal
    sheet.getRange("A2").setValue(json.symbol);
    sheet.getRange("B2").setValue(json.type);
    sheet.getRange("C2").setValue(json.strike);
    sheet.getRange("D2").setValue(json.ltp);
    sheet.getRange("E2").setValue(json.entry);
    sheet.getRange("F2").setValue(json.sl);
    sheet.getRange("G2").setValue(json.target);
    sheet.getRange("H2").setValue(json.volume);

    // âœ… Append to Logs tab
    logSheet.appendRow([
      new Date(),
      json.symbol,
      json.type,
      json.strike,
      json.ltp,
      json.entry,
      json.sl,
      json.target,
      json.volume
    ]);
  } else {
    sheet.getRange("A2").setValue("No trade found");
    sheet.getRange("B2:H2").clearContent();
  }
}
function clearLogsAtNight() {
  const logSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Logs");
  const lastRow = logSheet.getLastRow();
  if (lastRow > 1) {
    logSheet.deleteRows(2, lastRow - 1); // Keeps header row
  }
}
