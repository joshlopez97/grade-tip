from flask import current_app as app
from GradeTip.content.content import ContentStore
from GradeTip.content.identifier import NameProvider
from GradeTip.redis.set import RedisSet


class ReplyStore(ContentStore):
    def __init__(self, user_manager):
        super().__init__(["text"], "reply")
        self.user = user_manager
        self.name_provider = NameProvider()

    def request_reply(self, school_id, form_data):
        """
        Request to create a reply in a school's page.
        :param school_id: ID of school to make request
        :param form_data: raw form data submitted by user
        :return: request ID if successful, otherwise None
        """
        if not super().validate_data(form_data):
            return False

        # check if content exists that is being replied to
        content_id = form_data["content_id"]
        if content_id is None or not super().content_exists(content_id):
            return False

        # get new request_id
        request_id = self.name_provider.generate_request_id(super().user_email)
        if request_id is None:
            return False

        # store data
        return super().request_content(request_id, {
            "sid": school_id,
            "content_id": content_id,
            "text": form_data["text"],
            "uid": super().display_name,
            "email": super().user_email
        })

    def create_reply(self, request):
        """
        Create a reply to some content. Promotes reply request to reply.
        :param request: dict containing request data to promote
        :return: reply ID if successful, otherwise None
        """
        # get new reply_id
        school_id = request["sid"]
        user_email = request["email"]
        reply_id = self.name_provider.generate_reply_id(request["email"], request["content_id"])

        return super().make_content(reply_id, {
            "sid": school_id,
            "content_id": request["content_id"],
            "text": request["text"],
            "uid": request["uid"],
            "email": user_email,
            "time": request["time"]
        })

    def get_replies(self, content_id):
        """
        Get all existing replies for content with given ID
        :param content_id: ID of content
        :return: dict containing all replies
        """
        replies = {}
        reply_set_key = self.name_provider.set_names.reply(content_id)
        for reply_id in RedisSet(reply_set_key).values():
            replies[reply_id] = super().get_content(reply_id)
        app.logger.debug("fetched {} replies for content {}".format(len(replies), content_id))
        return replies

