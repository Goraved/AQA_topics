import logging

from data import query

# Set up logging
logger = logging.getLogger(__name__)

# Cache for domains list
_domains_cache = None
_domains_cache_valid = False


async def get_domains() -> list[str]:
    """
    Asynchronous function to get all domains from the whitelist.

    Returns:
        list[str]: A list of domain names.
    """
    global _domains_cache, _domains_cache_valid

    try:
        cur = query("SELECT domain FROM whitelist")
        domains = [_[0] for _ in cur.fetchall()]
        cur.close()

        # Update cache
        _domains_cache = domains
        _domains_cache_valid = True

        return domains
    except Exception as e:
        logger.error(f"Error in get_domains: {e}")
        return []


def check_link_in_whitelist(link: str) -> bool:
    """
    Check if a link is in the whitelist using the cached domains list when available for better performance.

    Args:
        link (str): The link to check.

    Returns:
        bool: True if the link is in the whitelist, False otherwise.
    """
    global _domains_cache, _domains_cache_valid

    try:
        domains = None

        # Use cache if valid
        if _domains_cache_valid and _domains_cache:
            domains = _domains_cache
        else:
            # Otherwise fetch from database
            domains = Domain.get_domains_list()

        for domain in domains:
            if domain in link:
                return True
        return False
    except Exception as e:
        logger.error(f"Error in check_link_in_whitelist: {e}")
        return False


class Domain:
    """
    A class to represent a domain.

    Attributes:
        name (str): The name of the domain.
    """

    def __init__(self, name: str):
        """
        Constructs all the necessary attributes for the domain object.

        Args:
            name (str): The name of the domain.
        """
        self.name = name

    @staticmethod
    def get_domains_list() -> list[str]:
        """
        Get the list of domains from the database.

        Returns:
            list[str]: A list of domain names.
        """
        global _domains_cache, _domains_cache_valid

        try:
            cur = query("SELECT domain FROM whitelist")
            domains = [_[0] for _ in cur.fetchall()]
            cur.close()

            # Update cache
            _domains_cache = domains
            _domains_cache_valid = True

            return domains
        except Exception as e:
            logger.error(f"Error in get_domains_list: {e}")
            return []

    def create_domain(self):
        """
        Add a new domain to the whitelist.
        """
        global _domains_cache_valid
        try:
            query(f"INSERT INTO whitelist VALUES ('{self.name}')")
            _domains_cache_valid = False  # Invalidate cache
        except Exception as e:
            logger.error(f"Error creating domain: {e}")

    def update_domain(self, new_domain: str):
        """
        Update a domain in the whitelist.

        Args:
            new_domain (str): The new domain name to update to.
        """
        global _domains_cache_valid
        try:
            query(f"UPDATE whitelist SET domain='{new_domain}' WHERE domain = '{self.name}'")
            _domains_cache_valid = False  # Invalidate cache
        except Exception as e:
            logger.error(f"Error updating domain: {e}")

    def remove_domain(self):
        """
        Remove a domain from the whitelist.
        """
        global _domains_cache_valid
        try:
            query(f"DELETE FROM whitelist WHERE domain = '{self.name}'")
            _domains_cache_valid = False  # Invalidate cache
        except Exception as e:
            logger.error(f"Error removing domain: {e}")
