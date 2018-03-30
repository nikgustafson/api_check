# test platform integrations: auth.net, shipping rates
import requests
import pytest

# auth.net


# shipping rates

# GetRates, GetLineItemRates, and SetShippingCost
# GetRates will automatically separate the Order's Line Items into shipments based on their ShippingAddress and the Line Item Product's ShipFromAddress. Rates will be returned based on these determined shipments.
# GetLineItemRates will obtain shipping rates for each Line Item individually, regardless of the item’s ShippingAddress and the Line Item Product’s ShipFromAddress.
# SetShippingCost simply allows your application to set an Order's ShippingCost value once the user has selected their desired shipper(s) for their Order.