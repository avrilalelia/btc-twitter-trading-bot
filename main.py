from nltk.sentiment import SentimentIntensityAnalyzer


class BTCTweetTradingBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 2, 5)
        self.SetEndDate(2021, 2, 6)
        self.SetCash(100000)

        self.btcusd = self.AddCrypto(
            "BTCUSD", Resolution.Minute, Market.Bitfinex).Symbol
        self.tweet = self.AddData(
            BTCTweet, "BTCTWTS", Resolution.Minute).Symbol

        self.Schedule.On(self.DateRules.EveryDay(self.btcusd),
                         self.TimeRules.At(22, 0),
                         self.ExitPositions)

    def OnData(self, data):
        if self.tweet in data:
            score = data[self.tweet].Value
            content = data[self.tweet].Tweet

            if score > 0.5:
                self.SetHoldings(self.btcusd, 1)
            elif score < -0.5:
                self.SetHoldings(self.btcusd, -1)

            if abs(score) > 0.0:
                self.Log("Score :" + str(score)+", Tweet :" + content)

    def ExitPositions(self):
        self.Liquidate()


class BTCTweet(PythonData):

    sia = SentimentIntensityAnalyzer()

    def GetSource(self, config, date, isLive):
        source = "https://www.dropbox.com/s/gxhkj5bidkdstrc/btc_tweets.csv?dl=1"
        return SubscriptionDataSource(source, SubscriptionTransportMedium.RemoteFile)

    def Reader(self, config, line, date, isLive):
        if not (line.strip() and line[0].isdigit()):
            return None

        data = line.split(',')

        tweet = BTCTweet()

        try:
            tweet.Symbol = config.Symbol
            tweet.Time = datetime.strptime(
                data[0], '%Y-%m-%d %H:%M:%S') + timedelta(minutes=1)

            content = data[1].lower()

            tweet.Value = self.sia.polarity_scores(content)["compound"]

            tweet["Tweet"] = str(content)
        except ValueError:
            return None

        return tweet
