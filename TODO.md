

---

## General

- [ ] properly mark all tests with descriptions
- [ ] add marks to collect all tests into 
    1. what can run in prod / qa
    2. different test suites
- [ ] connect to jira stories
- [ ] convert tests and modules to use sessions

## Message Senders

Possible values: 
- OrderDeclined
- ~~OrderSubmitted~~
- ShipmentCreated
- ~~ForgottenPassword~~ >> only ordercloud routed email, all other depend on mandrill/etc
- OrderSubmittedForYourApproval
- OrderSubmittedForApproval
- OrderApproved
- OrderSubmittedForYourApprovalHasBeenApproved
- OrderSubmittedForYourApprovalHasBeenDeclined
- NewUserInvitation

## Authorize.Net

## Shipping Rates

## OpenConnect ID

currently config must be manually set up per api client beforehand.

## Webhooks