from flask import Blueprint, jsonify
from flask_login import login_required

advice = Blueprint('advice', __name__)


@advice.route("/advice/<adviceTitle>", methods=["GET", "POST"])
@login_required
def adviceList(adviceTitle):
    
    if adviceTitle == 'CreateOEEAdvice':
        text = """<p>This section is where you create an OEE sheet for your shift.</p>
                <strong>Overview</strong>
                <ul>
                    <li>An OEE sheet must be created per individual shift.</li>
                    <li>A shift is classed as any 8 hour period.</li>
                    <li>A shift is per production line. 
                    If two lines are running, two OEE sheets need to be created.</li>
                </ul>

                <strong>How to:</strong>
                <ol>
                    <li>Click Add button.</li>
                    <li>Select line number & order number.</li>
                    <li>Enter line speed and number of total operators.</li>
                    <li>Click Save.</li>
                </ol>

                <strong>Order Number Info</strong>
                <p>An OEE sheet cannot be created without an order number. An order number will
                only be available if:</p>
                <ol>
                    <li>An order has been created</li>
                    <li>An orders status is not 'Complete'.</li>
                </ol>
                <p>Please note, the order status is automatically updated to 'Complete' if the total amount 
                produced is equal to, or greater than, the order quantity. You can view all available 
                orders, and their status, by visiting the Orders section. </p>

                <p>If you need to create another OEE sheet for a job that has a status of complete, 
                go to the Orders section, select the order and use the Edit button to update the status 
                to 'In Progress'.</p>
        """
        return text

    if adviceTitle == 'OEESheetAdvice':
        text = """
        <p>This sheet is designed to capture all of the events that happen throughout a shift.</p>
        <strong>Note</strong>
        <p>As a shift is classed as any 8 hour period, the start time of your shift doesn't matter.
        For example, if your shift starts at 9am, data missing for 7am and 8am will not affect
        any scores.</p>
        <strong>How To:</strong>
        <ol>
            <li>Select the hour period for your data.</li>
            <li>Choose what data you need to enter.</li>
            <li>Enter the amount. For products/rejects the amount 
            is the number of units. For downtime, the amount is minutes.</li>
            <li>Click Save.</li>
        </ol>
        <strong>Notes</strong>
        <p>The scores are updated as new data is entered, and are calculated against
        a full day.</p>


        """
        return text