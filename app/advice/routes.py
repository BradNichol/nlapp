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
                    <li>If two lines are running, two OEE sheets need to be created.</li>
                </ul>

                <strong>How to:</strong>
                <ol>
                    <li>Click Add button.</li>
                    <li>Select line number.</li>
                    <li>Enter line speed and number of total operators.</li>
                    <li>Click Save.</li>
                </ol>

                
        """
        

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

        <strong>Planned Output</strong>
        <p>The planned output value has been set by Scheduling, and against previously
        agreed targets.</p>


        """

    if adviceTitle == 'ScheduleOverviewAdvice':
        text = """
        <p>The weekly schedule is designed to give an overview of what products are to be produced each week,
        and on what line they'll be produced. </p>
        <p>This is also where you'll set the daily production target, that will inform the 
        Conformance To Plan (CTP) score.</p>
        
        <strong>How To:</strong>
        <ol>
            <li>Click Add Schedule Button.</li>
            <li>Select a week commencement date.</li>
            <li>Save.</li>
        </ol>

        <p>Click on the newly created date to view the schedule.</p>

        """
    
    if adviceTitle == 'ScheduleDetailAdvice':
        text = """
        <p>Here is where you'll set the production schedule for the chosen week.</p>

        <strong>How To:</strong>
        <ol>
            <li>Click Add Product button.</li>
            <li>Select a product and choose the line number for production.</li>
            <li>Click Save.</li>
            <li>Enter the planned output number for that product, each day.</li>
            <li>Make sure to press update once any changes have been made.</li>
        </ol>
        <strong>Product Notes</strong>
        <p>Once a product has been added for a particular production line, it cannot be added again.
        It can only be added against an another line number. This is to prevent duplication issues.</p>

        <strong>Notes on CTP</strong>
        <p>For CTP to be added and tracked against each shift, a prior schedule
        must have been setup and planned output entered.</p>
        <p>If the OEE sheet for that shift has already begun, adding planned output numbers
        afterwards, within the schedule, will have no affect on the score displayed on the 
        OEE sheet or other reports.</p>


        """
    return text