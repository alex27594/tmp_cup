from collections import namedtuple
from random import random

HourPublisherUserTriplet = namedtuple('HourPublisherUserTriplet', ['hour', 'publisher', 'user_id'])
CompetitorItem = namedtuple('CompetitorItem', ['ind', 'cmp'])
UserPublisherHourTriplet = namedtuple('UserPublisherHourTriplet', ['user_id', 'publisher', 'hour'])


class Prober:
    def fit(self, hist_df, users_df):
        tmp_df = hist_df[['hour', 'user_id', 'publisher']].set_index('user_id').join(
            users_df[['user_id', 'sex', 'age']].set_index('user_id')).reset_index()
        tmp_df['hour_class'] = tmp_df['hour'].apply(lambda item: HourStaticGuru.to_hour_class(item))
        tmp_df['age_class'] = tmp_df['age'].apply(lambda item: AgeStaticGuru.to_age_class(item))
        tmp_df.drop(columns=['hour', 'age'])

        self.users_df = tmp_df[['uer_id', 'age_class', 'sex']]

        null_sex_df = tmp_df[tmp_df.sex == 0]
        null_age_df = tmp_df[tmp_df.age_class == 0]

        res_df = tmp_df.copy()
        for cur_sex in SexStaticGuru.get_sex_types():
            class_size = min(tmp_df[tmp_df.sex == cur_sex], 1)
            cur_sex_df = null_sex_df.copy().sample(n=class_size, replace=True)
            cur_sex_df['sex'] = cur_sex
            res_df = res_df.append(cur_sex_df, ignore_index=True)

        for cur_age_class in AgeStaticGuru.get_age_types():
            class_size = min(tmp_df[tmp_df.age_class == cur_age_class], 1)
            cur_age_class_df = null_age_df.copy().sample(n=class_size, replace=True)
            cur_age_class_df['age_class'] = cur_age_class
            res_df = res_df.append(cur_age_class_df, ignore_index=True)

        in_count_reset_index_df = tmp_df.groupby(['hour_class', 'publisher', 'age_class', 'sex'])[
            ['user_id']].nuniuqe().reset_index()
        all_count_df = tmp_df.groupby(['publisher', 'age_class', 'sex'])[['user_id']].nunique()

        rel_df = in_count_reset_index_df.set_index(['publisher', 'age_class', 'sex']).join(all_count_df, lsuffix='_in',
                                                                                           rsuffix='_all').reset_index()
        rel_df['prob'] = rel_df['user_id_in'] / rel_df['user_id']
        self.rel_df = rel_df[['hour_class', 'publisher', 'age_class', 'sex']]

    def _get_prob(self, hour_class, age_class, publisher, sex):
        return self.rel_df[(self.rel_df.hour_class == hour_class) & (self.rel_df.age_class == age_class) & (
                    self.rel_df.publisher == publisher) & (self.rel_df.sex == sex)]

    def get_sample(self, user_id, publisher, hour):
        age_class, sex = self.users_df[self.users_df.user_id == user_id].iloc[0]
        hour_class = HourStaticGuru.to_hour_class(hour)
        prob = self._get_prob(hour_class, age_class, publisher, sex)
        return int(random() < prob)


class CompetitorsGuru:
    def fit(self, val_df):
        self.res = {}
        for i in range(val_df.shape[0]):
            cur_hour_start, cur_hour_end = val_df.loc[i, ['hour_start', 'hour_end']]
            cur_publishers = list(map(int, val_df.loc[0, 'publishers'].split(',')))
            cur_users = list(map(int, val_df.loc[0, 'users'].split(',')))
            cur_cmp = val_df.loc[i, 'cmp']
            for h in range(cur_hour_start, cur_hour_end + 1):
                for p in cur_publishers:
                    for u in cur_users:
                        ind = HourPublisherUserTriplet(h, p, u)
                        if ind not in self.res:
                            self.res[ind] = []
                        self.res[ind].append(CompetitorItem(i, cur_cmp))


class UsersGuru:
    def __init__(self, prober):
        self.prober = prober
        self.cache = {}

    def get_user(self, user_id, publisher, hour):
        ind = UserPublisherHourTriplet(user_id, publisher, hour)
        if ind not in self.cache:
            self.cache[ind] = self.prober.get_sample(user_id, publisher, hour)
        return self.cache[ind]


class Model:
    def fit(self, hist_df, users_df):
        self.prober = Prober(hist_df, users_df)
        self.unique_publishers = list(hist_df.publishers.unique())
        self.unique_users = list(host_df)

    def sim(self, val_df):
        start = val_df['hour_start'].min()
        end = val_df['hour_end'].max()
        unique_publishers = val_df['']
        compGuru = CompetitorsGuru.fit(val_df)
        for h in range(start, end + 1):
            for p in self.unique_publishers:
                for u in

