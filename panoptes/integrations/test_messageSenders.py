#! tests_messageSenders.py


import pytest
import requests
from requests import codes
import logging
import json
import time
from faker import Faker
from random import randint, choice, randrange


from .. import me
from .. import auth
from .. import integrations
from ..integrations import listServers, listEmails, findEmail, awaitEmail, getEmail, deleteEmail, resetEmail
from ..users import createUser
from ..orders import orderCreate

from ..me import registerMe, get_Me

from mailosaur import MailosaurClient
from mailosaur.models import SearchCriteria


fake = Faker()
log = logging.getLogger(__name__)


"""
variation: user types
	- anon buyer user who does not register
	- anon buyer user who does register (after order create)
	- previously registered buyer user
	- registered admin user in buyer app
"""


@pytest.mark.smoke
@pytest.mark.description("Verifies that the ForgottenPassword message sender successfully sends an email when triggered. NOTE: this message sender is only triggered by the '/v1/password/reset' endpoint.")
def test_ForgottenPassword(configInfo):
    """
    verifies that Forgotten Password (Password Reset) emails are sent and recieved for Ordercloud application users.
    """
    client_id = configInfo['BUYER-CLIENTID']
    username = configInfo['BUYER-USERNAME']
    password = configInfo['BUYER-PASSWORD']
    scope = ['Shopper', 'MeAdmin']

    # auth as buyer user
    token = auth.get_Token_UsernamePassword(
        configInfo, client_id, username, password, scope)

    resetUrl = fake.url()

    user = me.get_Me(configInfo, token['access_token'])
    userEmail = user['Email']

    # make sure the user has the right email server
    if configInfo['MAILOSAUR-SERVER'] not in userEmail:

        newEmail = {'Email': user['Username'] + '.' +
                    configInfo['MAILOSAUR-SERVER'] + '@mailosaur.io'}
        log.debug(newEmail)

        user = me.patch_Me(configInfo, token, newUser=newEmail)
        log.debug(user)

        userEmail = user['Email']

    # reset that password!
    log.info('reset that password!')
    resetcall = auth.post_resetPassword(configInfo, token, resetUrl)

    # get that email
    # time.sleep(300)

    log.info('time to get the email')

    client = MailosaurClient(configInfo['MAILOSAUR-KEY'])

    pwEmailSubject = 'Here is the link to reset your password'

    email = awaitEmail(configInfo, subject=pwEmailSubject,
                       sentTo=userEmail, body=None)

    # log.info(json.dumps(email, indent=4))

    if email is codes.no_content:
        pytest.fail(msg='The email was not found on the email server.')
        log.info('NO EMAIL FOUND!')
    else:
        emailID = email['id']
        # log.info(email.keys())

    # get email

    checkEmail = getEmail(configInfo, emailID)

    assert checkEmail['subject'] == pwEmailSubject
    assert checkEmail['to'][0]['email'] == userEmail
    assert 'Password Reset' in checkEmail['text']['body']

    # log.info(checkEmail['text'])

    # delete email

    deleteEmail(configInfo, emailID)


@pytest.mark.skip
@pytest.mark.description(
    "Verifies that the NewUserInvited message sender is working for Registered users.")
def test_NewUserInvitedRegister(configInfo, connections):
    """

    """

    # anon user register

    user = connections['anon'].get(
        configInfo['API'] + 'v1/me')

    userEmail = user.json()['Email']

    # make sure the email is set to mailosaur
    newEmail = resetEmail(configInfo, connections, user.json())

    assert user.json()['ID'] == 'anon-template'

    registeredUser = registerMe(configInfo, connections['anon'])
    log.info(json.dumps(registeredUser, indent=4))

    registeredUser = get_Me(configInfo, registeredUser['access_token'])
    log.info(registeredUser)

    # get that email
    # time.sleep(300)

    log.info('time to get the email')

    client = MailosaurClient(configInfo['MAILOSAUR-KEY'])

    inviteEmailSubject = 'You\'ve been invited to Ordercloud!'

    email = awaitEmail(configInfo, subject=inviteEmailSubject,
                       sentTo=registeredUser['Email'], body=None)

    log.info(email)


@pytest.mark.skip
@pytest.mark.description(
    "Verifies that the NewUserInvited message sender is working for created users.")
def test_NewUserInvitedCreated(configInfo, connections):
    """

    """

    # create a new user with admin

    user = createUser(configInfo, connections['admin'])

    registeredUser = registerMe(configInfo, connections['anon'])
    log.info(json.dumps(registeredUser, indent=4))

    registeredUser = get_Me(configInfo, registeredUser['access_token'])
    log.info(registeredUser)

    # get that email
    # time.sleep(300)

    log.info('time to get the email')

    client = MailosaurClient(configInfo['MAILOSAUR-KEY'])

    inviteEmailSubject = 'You\'ve been invited to Ordercloud!'

    email = awaitEmail(configInfo, subject=inviteEmailSubject,
                       sentTo=registeredUser['Email'], body=None)

    log.info(email)


@pytest.mark.smoke
@pytest.mark.description(
        "Verifies that the OrderSubmitted message sender is working. \
	Test registers an Anon User, creates an order with lineitem, and submits the order. After order submit, test verifies that an OrderSubmitted email was recieved by the order submitting user.")
def test_OrderSubmitted(configInfo, connections):
    """
    verifies that Order Submit emails are being sent for the following types of users:
            1. Anon Users who do not register during checkout
            2. Anon Users who register during checkout process (after order is created)
            3. Previously registered buyer users
    returns: nothing
    """
    buyer = connections['buyer']

    orders = buyer.get(configInfo['API'] +
                       'v1/me/orders', params={'IsSubmitted': False, 'LineItemCount': '>=1'})
    # log.info(orders.status_code)
    # log.info(orders.json())
    assert orders.status_code is codes.ok

    if orders.json()['Meta']['TotalCount'] == 0:
        newOrder = orderCreate(configInfo, buyer, 'outgoing', {"Comments": ""})
        # log.info(newOrder)
        orders = buyer.get(configInfo['API'] +
                           'v1/me/orders', params={'IsSubmitted': False})
    # log.info(orders.json()['Items'])

    items = orders.json()['Items']
    assert len(items) > 0

    totalCount = orders.json()['Meta']['TotalCount']
    #log.info("TOTAL COUNT = " + str(totalCount))
    assert totalCount > 0

    randomOrder = randrange(orders.json()['Meta']['PageSize'] - 1)
    # log.info("Random Order # = " + str(randomOrder))

    getOrder = orders.json()['Items'][randomOrder]
    # log.info(getOrder)
    orderID = getOrder['ID']
    # log.info(orderID)

    if getOrder['LineItemCount'] == 0:
        log.info('Need a new lineitem!')

        meProducts = buyer.get(configInfo['API'] + 'v1/me/products')
        # log.info(meProducts.json())
        randProduct = choice(meProducts.json()['Items'])
        # log.info(randProduct)
        randQuant = randrange(randProduct['PriceSchedule']['MinQuantity'], randProduct[
                              'PriceSchedule']['MaxQuantity'])
        meAddresses = buyer.get(configInfo['API'] + 'v1/me/addresses')

        log.info(randQuant)
        # create line item
        lineBody = {
            "ProductID": randProduct['ID'],
            "Quantity": randQuant,
            "DateNeeded": '',
            "xp": {}
        }

        if meAddresses.json()['Meta']['TotalCount'] > 0:
            # set shipping address
            lineBody['ShippingAddress'] = choice(meAddresses.json()['Items'])
        log.info(lineBody)

        newLineItem = buyer.post(
            configInfo['API'] + 'v1/orders/outgoing/' + orderID + '/lineitems', json=lineBody)
        # log.info(newLineItem.json())
        assert newLineItem.status_code is codes.created

    assert buyer.get(configInfo['API'] +
                     'v1/orders/outgoing/' + orderID).json()['LineItemCount'] > 0
    lineitems = buyer.get(
        configInfo['API'] + 'v1/orders/outgoing/' + orderID + '/lineitems')
    assert lineitems.status_code is codes.ok
    #log.info(json.dumps(lineitems.json()['Items'], indent=4))

    products = []
    for item in lineitems.json()['Items']:
        log.info(item['ProductID'])
        line = item['ProductID']
        products.append(line)
    # log.info(products)

    # submit order

    orderSubmitted = buyer.post(configInfo['API'] +
                                'v1/orders/outgoing/' + orderID + '/submit')

    assert orderSubmitted.status_code is codes.created
    assert orderSubmitted.json()['IsSubmitted'] == True
    assert orderSubmitted.json()['Status'] == 'Open'

    # verify email

    userEmail = orderSubmitted.json()['FromUser']['Email']

    log.info('time to get the email')

    client = MailosaurClient(configInfo['MAILOSAUR-KEY'])

    pwEmailSubject = 'Hey, thanks for the order'

    email = awaitEmail(configInfo, subject=pwEmailSubject,
                       sentTo=userEmail, body=None)

    # log.info(json.dumps(email, indent=4))

    if email is codes.no_content:
        pytest.fail(msg='The email was not found on the email server.')
        log.info('NO EMAIL FOUND!')
    else:
        emailID = email['id']
        # log.info(email.keys())

    # get email

    checkEmail = getEmail(configInfo, emailID)

    assert checkEmail['subject'] == pwEmailSubject
    assert checkEmail['to'][0]['email'] == userEmail
    assert 'Your order has been received' in checkEmail['text']['body']
    assert orderID in checkEmail['text']['body']

    for product in products:
        assert product in checkEmail['text']['body']

    log.info(checkEmail['text'])

    # delete email

    deleteEmail(configInfo, emailID)


def test_ShipmentCreated(configInfo, connections):
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """

    # auth as user
    buyer = connections['buyer']
    admin = connections['admin']

    # select an unshipped order

    pass


@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderApproved message sender email.\
	CURRENTLY A STUB.")
def test_OrderApproved():
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """
    pass


@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderDeclined message sender email.\
	CURRENTLY A STUB.")
def test_OrderDeclined():
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """
    pass


@pytest.mark.description("Verifies that User who submitted an order for approval recieves OrderSubmittedForApproval message sender email.\
	CURRENTLY A STUB.")
def test_OrderSubmittedForApproval():
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """
    pass


def test_OrderSubmittedForYourApprovalHasBeenApproved():
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """
    pass


def test_OrderSubmittedForYourApprovalHasBeenDeclined():
    """
    emails should be sent for Ordercloud application users.
    returns: nothing
    """
    pass
