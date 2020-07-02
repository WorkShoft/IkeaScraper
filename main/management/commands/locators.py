from selenium.webdriver.common.by import By


class ManySofaLocators(object):
    """
    Locators for sofa list pages
    """

    NAME = (By.CLASS_NAME, "product-compact__name")
    TYPE = (By.CLASS_NAME, "product-compact__type")
    IMAGE = (By.XPATH, "//div[@class='range-image-claim-height']/img")


class SingleSofaLocators(object):
    """
    Locators for individual sofa views and variation modals
    """

    COLOR = (By.CLASS_NAME, "range-product-variation__label")


class SofaTypeListLocators(object):
    NUMBER_OF_ITEMS = (By.CLASS_NAME, "catalog-filter__total-count")
