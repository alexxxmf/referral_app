
function do_build {
    PROJECT=$1

    #remove .pyc files
    find . -iname "*.pyc" -exec rm {} \;

    PYTHONPATH=referral_app pytest --ds=referral_app.settings --cov=${PROJECT} --flake8 

}

do_build referral_app
