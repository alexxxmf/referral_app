from pyshorteners import Shortener

def relative_progress(subscriber, rewards=None, stage=1):
    '''
    This helper function is going to give us the relative relative_progress
    for a given subscriber and given set of rewards to then represent in
    graphically via Javascript in the template
    '''
    if len(rewards) == 0:
        return 0
    else:
        reward_ref_count_list = sorted([re.referrals_needed for re in rewards])

        for reward_ref_count in reward_ref_count_list:
            if subscriber.referral_count > reward_ref_count:
                stage += 1
                continue
            else:
                width = 25 + (
                    (subscriber.referral_count / reward_ref_count) * (
                        (stage * (100 - 25) / len(rewards))
                    )
                )
                width = int(width)

        return width

# this is the python library that contains the most popular url shorteners from the market
# IMPORTANT NOTE: For most of them we need credentials. In this case tinyurl is an exception but
# it's better to be aware of it

def url_shortener(url):
    '''
    This fuction is going to shorten the provided url to make it more
    user-friendly
    '''
    shortener = Shortener('Tinyurl')
    shortened_url = shortener.short(url)
    return shortened_url
