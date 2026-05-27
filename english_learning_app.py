import streamlit as st
import streamlit.components.v1 as components
import anthropic
import base64
import json
import re
import hashlib
import datetime
import requests

# ══════════════════════════════════════════════
#  CONFIGURATION  (გასაღებები st.secrets-შია)
# ══════════════════════════════════════════════
MODEL = "claude-sonnet-4-6"

# ══════════════════════════════════════════════
#  CURRICULUM DATA (8 weeks × 4 lessons)
# ══════════════════════════════════════════════
CURRICULUM = [
    {"week":1,"emoji":"👋","color":"#6366f1","title":"პირველი ნაბიჯები","theme":"Greetings & Basics","lessons":[
        {"id":"w1l1","emoji":"🤝","title":"Introductions","geo":"გაცნობა",
         "scenario":"You arrive at an international event in Tbilisi. Time to meet new people! 🌍",
         "phrases":["Nice to meet you!","My name is ___.","I'm from Georgia.","What do you do for a living?","It's a pleasure!","How long have you been here?"],
         "vocab":[{"w":"introduce","g":"გაცნობება","p":"ინთ-რო-დიუს"},{"w":"pleasure","g":"სიამოვნება","p":"პლე-ჟერ"},{"w":"profession","g":"პროფესია","p":"პრო-ფე-შენ"},{"w":"background","g":"წარმომავლობა","p":"ბექ-გრაუნდ"}],
         "dialogue":[("😊 Alex","Hi! I don't think we've met. I'm Alex."),("🇬🇪 You","Nice to meet you, Alex! I'm Giorgi, from Tbilisi."),("😊 Alex","Oh wow, Georgia! What do you do?"),("🇬🇪 You","I'm a developer. What about you?"),("😊 Alex","I'm a teacher. Welcome to the event!")],
         "practice":"We just met at an international event! Introduce yourself — your name, where you're from, and what you do. I'll be your new acquaintance. 😊"},
        {"id":"w1l2","emoji":"🕐","title":"Time & Numbers","geo":"დრო და ციფრები",
         "scenario":"Your friend asks when to meet. Handle times, dates and numbers! ⏰",
         "phrases":["What time is it?","It's half past three.","Let's meet at 7 PM.","What's the date today?","It's the 15th of May.","See you tomorrow!"],
         "vocab":[{"w":"quarter","g":"მეოთხედი","p":"ქვო-ტე"},{"w":"midnight","g":"შუაღამე","p":"მიდ-ნაიტ"},{"w":"schedule","g":"გრაფიკი","p":"სქე-ჯულ"},{"w":"appointment","g":"შეხვედრა","p":"ა-პოინტ-მენტ"}],
         "dialogue":[("📱 Sam","Hey, when should we meet?"),("🇬🇪 You","How about Saturday at half past two?"),("📱 Sam","That's the 22nd, right? Perfect!"),("🇬🇪 You","Yes! Let's meet at the coffee shop."),("📱 Sam","Great, see you then! Don't be late! 😄")],
         "practice":"Let's practice scheduling! I'll ask you about times and dates for a meeting we need to arrange. 📅"},
        {"id":"w1l3","emoji":"🗺️","title":"Asking Directions","geo":"მიმართულებები",
         "scenario":"You're a tourist in London, lost near a big station. Find your way! 🏙️",
         "phrases":["Excuse me, where is the subway?","Turn left/right at the corner.","It's straight ahead.","How far is it?","Is it within walking distance?","Take the second right."],
         "vocab":[{"w":"intersection","g":"გზაჯვარედინი","p":"ინ-თე-სექ-შენ"},{"w":"landmark","g":"ორიენტირი","p":"ლენდ-მა-ქ"},{"w":"block","g":"კვარტალი","p":"ბლოქ"},{"w":"roundabout","g":"რგოლი","p":"რაუნდ-ა-ბაუთ"}],
         "dialogue":[("🇬🇪 You","Excuse me, is there a pharmacy nearby?"),("🏙️ Local","Yes! Go straight two blocks, then turn left."),("🇬🇪 You","Past the big church?"),("🏙️ Local","Exactly! You can't miss it."),("🇬🇪 You","Thank you so much!")],
         "practice":"You're lost in London near Big Ben! Ask me (a friendly local) for directions to the nearest underground station. 🗺️"},
        {"id":"w1l4","emoji":"👤","title":"Describing People","geo":"ადამიანების აღწერა",
         "scenario":"Help your friend find someone at a crowded party. 🎉",
         "phrases":["She's tall with dark hair.","He's wearing a blue jacket.","She looks around 30.","He has a beard.","She's the one near the window.","He's quite slim."],
         "vocab":[{"w":"appearance","g":"გარეგნობა","p":"ა-პი-რენს"},{"w":"curly","g":"კულულებიანი","p":"ქე-ლი"},{"w":"distinguish","g":"გამოარჩევა","p":"დის-თინ-გუიშ"},{"w":"recognise","g":"ამოცნობა","p":"რე-კოგ-ნაიზ"}],
         "dialogue":[("📱 Friend","I can't find Maya. What does she look like?"),("🇬🇪 You","She's medium height with long curly hair."),("📱 Friend","What's she wearing?"),("🇬🇪 You","A red dress and white shoes."),("📱 Friend","Oh! I see her by the door!")],
         "practice":"Describe an imaginary person at a party so I can find them! Include hair, height, clothing, and anything distinctive. 🎉"},
    ]},
    {"week":2,"emoji":"🏠","color":"#8b5cf6","title":"ყოველდღიური ცხოვრება","theme":"Daily Life","lessons":[
        {"id":"w2l1","emoji":"🌅","title":"Morning Routine","geo":"დილის რუტინი",
         "scenario":"Chat with a friend about daily morning habits. 🌞",
         "phrases":["I usually wake up at 7.","I skip breakfast sometimes.","I take a shower first thing.","The commute takes 30 minutes.","I grab a coffee on the way.","I start work at 9 sharp."],
         "vocab":[{"w":"routine","g":"რუტინი","p":"რუ-თინ"},{"w":"commute","g":"სამუშაოზე მგზავრობა","p":"კო-მიუთ"},{"w":"hectic","g":"ქაოტური","p":"ჰეq-თიq"},{"w":"prioritise","g":"პრიორიტეტი","p":"პრაი-ო-რი-თაიზ"}],
         "dialogue":[("☕ Friend","Are you a morning person?"),("🇬🇪 You","Not really! I struggle to wake up before 8."),("☕ Friend","Me too! What's your morning routine?"),("🇬🇪 You","Shower, coffee, then check my phone. Nothing exciting!"),("☕ Friend","Same! Mornings are hectic, aren't they?")],
         "practice":"Tell me about your morning routine! I'll ask questions about what you do each morning. ☀️"},
        {"id":"w2l2","emoji":"🛒","title":"At the Supermarket","geo":"სუპერმარკეტში",
         "scenario":"You can't find what you need. Ask the staff for help! 🏪",
         "phrases":["Excuse me, where are the dairy products?","Is this on sale?","I'm looking for...","Do you have this in stock?","Can I get a bag please?","Where do I pay?"],
         "vocab":[{"w":"aisle","g":"მწკრივი","p":"აილ"},{"w":"receipt","g":"ქვითარი","p":"რი-სიით"},{"w":"checkout","g":"სალარო","p":"ჩეq-აუთ"},{"w":"organic","g":"ორგანული","p":"ო-გე-ნიq"}],
         "dialogue":[("🇬🇪 You","Excuse me, where can I find olive oil?"),("🏪 Staff","It's in aisle 5, next to the pasta."),("🇬🇪 You","Thanks! Is this brand on sale?"),("🏪 Staff","Yes, it's 20% off today!"),("🇬🇪 You","Perfect, I'll take two!")],
         "practice":"You're in a supermarket and need help finding 3 items! Ask me (the staff) for help. 🛒"},
        {"id":"w2l3","emoji":"🏡","title":"Home & Living","geo":"სახლი",
         "scenario":"A friend visits your home for the first time. Show them around! 🚪",
         "phrases":["Welcome to my place!","Make yourself at home.","The kitchen is down the hall.","Can I get you something to drink?","This is the guest room.","Feel free to use anything."],
         "vocab":[{"w":"cosy","g":"მყუდრო","p":"კო-ზი"},{"w":"renovate","g":"გარემონტება","p":"რე-ნო-ვეიტ"},{"w":"landlord","g":"მეიჯარე","p":"ლენდ-ლოდ"},{"w":"utilities","g":"კომუნალური","p":"იუ-თი-ლი-თიზ"}],
         "dialogue":[("🏠 You","Welcome! Come in, come in!"),("👋 Guest","Thanks! Wow, your place is so cosy!"),("🏠 You","Thank you! Can I get you something to drink?"),("👋 Guest","Just water please. How long have you lived here?"),("🏠 You","Two years. I love this neighbourhood!")],
         "practice":"Give me a tour of your home! Describe each room as if I'm your guest visiting for the first time. 🏡"},
        {"id":"w2l4","emoji":"👨‍👩‍👧","title":"Family & Relationships","geo":"ოჯახი",
         "scenario":"Chat with a colleague about family life. 💬",
         "phrases":["I have a big family.","My sister lives abroad.","We're very close.","I'm an only child.","My parents are retired.","We get together at holidays."],
         "vocab":[{"w":"sibling","g":"და-ძმა","p":"სიბ-ლინგ"},{"w":"relative","g":"ნათესავი","p":"რე-ლა-თივ"},{"w":"upbringing","g":"აღზრდა","p":"აფ-ბრინ-ინგ"},{"w":"close-knit","g":"მჭიდრო ოჯახი","p":"კლოუს-ნიტ"}],
         "dialogue":[("💼 Colleague","Do you have any brothers or sisters?"),("🇬🇪 You","Yes, I have an older brother and a younger sister."),("💼 Colleague","Are you close?"),("🇬🇪 You","Very! We talk every day. My sister lives in Batumi though."),("💼 Colleague","That's sweet. Family is everything!")],
         "practice":"Tell me about your family! I'll ask questions about your siblings, parents and traditions. 👨‍👩‍👧‍👦"},
    ]},
    {"week":3,"emoji":"🍽️","color":"#ec4899","title":"საჭმელი და რესტორანი","theme":"Food & Dining","lessons":[
        {"id":"w3l1","emoji":"☕","title":"At the Café","geo":"კაფეში",
         "scenario":"Order drinks and snacks at a London café. ☕",
         "phrases":["I'd like a large latte, please.","Can I have it to go?","Do you have oat milk?","What's today's special?","Keep the change.","Can I get the Wi-Fi password?"],
         "vocab":[{"w":"barista","g":"ბარისტა","p":"ბა-რის-თა"},{"w":"decaf","g":"უკოფეინო","p":"დი-კეფ"},{"w":"pastry","g":"საცხობი","p":"პეის-თრი"},{"w":"takeaway","g":"წასასვლელი","p":"თეიq-ა-ვეი"}],
         "dialogue":[("🇬🇪 You","Hi! Can I get a medium flat white, please?"),("☕ Barista","Of course! Any milk preference?"),("🇬🇪 You","Oat milk if you have it."),("☕ Barista","We do! Anything to eat?"),("🇬🇪 You","I'll take a blueberry muffin too, please.")],
         "practice":"Walk into a busy London café and order your perfect coffee and snack from me (the barista)! ☕"},
        {"id":"w3l2","emoji":"🍷","title":"At the Restaurant","geo":"რესტორანში",
         "scenario":"A special dinner at a nice restaurant. Order, ask questions, pay the bill! 🍷",
         "phrases":["Can we have a table for two?","What do you recommend?","I'm allergic to nuts.","Could we get the bill, please?","Is service included?","I'd like to see the menu."],
         "vocab":[{"w":"reservation","g":"ჯავშანი","p":"რე-ზე-ვეი-შენ"},{"w":"appetiser","g":"წინა კერძი","p":"ე-პი-თაი-ზე"},{"w":"medium-rare","g":"ნახევრად მოხარშული","p":"მი-დიამ-რეა"},{"w":"complimentary","g":"უფასო (საჩუქრად)","p":"კომ-პლი-მენ-თა-რი"}],
         "dialogue":[("🇬🇪 You","Good evening. Do you have a reservation for two under 'Giorgi'?"),("🍽️ Waiter","Yes, right this way! Can I start you with some drinks?"),("🇬🇪 You","Yes, sparkling water and a glass of house red, please."),("🍽️ Waiter","Tonight's special is sea bass with capers."),("🇬🇪 You","That sounds lovely. I'll have that, please.")],
         "practice":"You're at a fancy restaurant! I'm your waiter. Order a starter, main and dessert, and ask for recommendations! 🍽️"},
        {"id":"w3l3","emoji":"🧑‍🍳","title":"Cooking & Recipes","geo":"სამზარეულო",
         "scenario":"Your flatmate wants to know how to make your favourite dish. Explain it! 🇬🇪",
         "phrases":["First, preheat the oven to 200°C.","Add a pinch of salt.","Let it simmer for 20 minutes.","You'll need half a kilo of...","Stir it occasionally.","Serve it hot!"],
         "vocab":[{"w":"ingredient","g":"ინგრედიენტი","p":"ინ-გრი-დიენთ"},{"w":"marinate","g":"მარინირება","p":"მა-რი-ნეიტ"},{"w":"simmer","g":"ნელ ცეცხლზე ადუღება","p":"სი-მე"},{"w":"garnish","g":"მორთვა (კერძის)","p":"გა-ნიშ"}],
         "dialogue":[("🏠 Flatmate","This smells amazing! What are you making?"),("🇬🇪 You","Khinkali! Georgian dumplings."),("🏠 Flatmate","How do you make them?"),("🇬🇪 You","You make a dough, fill it with spiced meat, then twist the top."),("🏠 Flatmate","Can you teach me? I need to learn this!")],
         "practice":"Teach me to cook something! Explain a simple recipe step by step — Georgian, Italian, anything. I'll ask questions! 🧑‍🍳"},
        {"id":"w3l4","emoji":"😋","title":"Talking About Food","geo":"საჭმელზე საუბარი",
         "scenario":"Discuss food preferences, diets and favourite cuisines with a friend. 😋",
         "phrases":["I'm a vegetarian.","I can't stand spicy food.","I'm absolutely addicted to...","What's your comfort food?","I eat out about twice a week.","Have you ever tried Ethiopian food?"],
         "vocab":[{"w":"cuisine","g":"სამზარეულო (ეროვნული)","p":"ქვი-ზინ"},{"w":"portion","g":"პორცია","p":"პო-შენ"},{"w":"savoury","g":"მარილიანი გემო","p":"სეი-ვე-რი"},{"w":"indulge","g":"სიამოვნება (საჭმლის)","p":"ინ-დალჯ"}],
         "dialogue":[("👫 Friend","Are you a picky eater?"),("🇬🇪 You","A little! I love Georgian food obviously, but I hate anything too sweet."),("👫 Friend","What about spicy food?"),("🇬🇪 You","Love it! The spicier, the better."),("👫 Friend","Ha! Me too. Have you tried Korean BBQ?")],
         "practice":"Tell me about your food preferences and favourite cuisine. What would you order if money was no object? 😋"},
    ]},
    {"week":4,"emoji":"✈️","color":"#f59e0b","title":"მოგზაურობა","theme":"Travel & Transport","lessons":[
        {"id":"w4l1","emoji":"✈️","title":"At the Airport","geo":"აეროპორტში",
         "scenario":"Flying to London for the first time. Navigate the airport confidently! 🛫",
         "phrases":["Where is the check-in desk?","I have two pieces of luggage.","Is this flight on time?","I'd like a window seat.","Where do I collect my bags?","My luggage is missing!"],
         "vocab":[{"w":"boarding pass","g":"ჩასხდომის ბარათი","p":"ბო-დინ პას"},{"w":"layover","g":"გადაჯდომა","p":"ლეი-ო-ვე"},{"w":"customs","g":"საბაჟო","p":"კას-თამს"},{"w":"departure","g":"გამგზავრება","p":"დი-პა-ჩე"}],
         "dialogue":[("🇬🇪 You","Excuse me, where is gate 14B?"),("✈️ Staff","Go straight, then turn left at the duty-free."),("🇬🇪 You","Thanks. Is the London flight on time?"),("✈️ Staff","There's a 20-minute delay, but it should be fine."),("🇬🇪 You","Okay, no problem. Thank you!")],
         "practice":"You're at a busy international airport! Ask me (airport staff) for help checking in, finding your gate, and asking about delays. ✈️"},
        {"id":"w4l2","emoji":"🚇","title":"Public Transport","geo":"საზოგადოებრივი ტრანსპორტი",
         "scenario":"Navigate the London Underground (Tube) for the first time. 🚇",
         "phrases":["Which line goes to Heathrow?","Can I use my card to pay?","Is this the right platform?","How many stops is it?","Do I need to change trains?","Excuse me, is this seat taken?"],
         "vocab":[{"w":"platform","g":"ჩიხური","p":"პლათ-ფო-მ"},{"w":"return ticket","g":"ორმხრივი ბილეთი","p":"რი-თე-ნ თი-ქეთ"},{"w":"rush hour","g":"საჭირბოროტო საათი","p":"რაშ ა-ვე"},{"w":"transfer","g":"გადაჯდომა","p":"თ-რენს-ფე"}],
         "dialogue":[("🇬🇪 You","Excuse me, does this train go to Oxford Circus?"),("🚆 Commuter","No, you need the Central line. Change at Bank."),("🇬🇪 You","How many stops to Bank?"),("🚆 Commuter","Just two stops. Quick journey!"),("🇬🇪 You","Perfect, thank you so much!")],
         "practice":"Navigate the London Underground! Ask me how to get from Victoria station to the British Museum. I'm a helpful local. 🚇"},
        {"id":"w4l3","emoji":"🏨","title":"Booking a Hotel","geo":"სასტუმრო",
         "scenario":"Book a room and deal with a small problem on arrival. 🛎️",
         "phrases":["I'd like to book a room for two nights.","Is breakfast included?","I have a booking under...","The room isn't clean.","Can I have a wake-up call at 7?","Can I check out late?"],
         "vocab":[{"w":"concierge","g":"კონსიერჟი","p":"კონ-სიე-ჟ"},{"w":"amenities","g":"კომფორტი","p":"ა-მე-ნი-თიზ"},{"w":"double room","g":"ორადგილიანი ოთახი","p":"და-ბელ რუმ"},{"w":"complain","g":"ჩივილი","p":"კომ-პლეინ"}],
         "dialogue":[("🇬🇪 You","Good afternoon. I have a reservation under 'Giorgi'."),("🏨 Receptionist","Welcome! Could I see your passport, please?"),("🇬🇪 You","Of course. Is the room ready?"),("🏨 Receptionist","It is! Room 304. Breakfast is at 7."),("🇬🇪 You","Great. Is there free Wi-Fi?")],
         "practice":"Call a hotel and book a room for 3 nights! Ask about prices, breakfast and amenities. I'm the receptionist. 🏨"},
        {"id":"w4l4","emoji":"🗼","title":"Sightseeing","geo":"ტურიზმი",
         "scenario":"Plan your London sightseeing at a tourist information centre. 🏰",
         "phrases":["What would you recommend for a first-time visitor?","How much is the entrance fee?","Are there guided tours?","What are the opening hours?","Can I buy tickets online?","Is it far from here?"],
         "vocab":[{"w":"itinerary","g":"მარშრუტი","p":"ი-თი-ნე-რა-რი"},{"w":"exhibit","g":"ექსპოზიცია","p":"იგ-ზი-ბიტ"},{"w":"scenic","g":"ლამაზი ხედით","p":"სი-ნიq"},{"w":"heritage","g":"მემკვიდრეობა","p":"ჰე-რი-თეჯ"}],
         "dialogue":[("🇬🇪 You","Hi, I'm visiting London for three days. What shouldn't I miss?"),("🗺️ Guide","Definitely the British Museum — it's free! And Tower Bridge."),("🇬🇪 You","Are there any guided walking tours?"),("🗺️ Guide","Yes! There's one every morning at 10 from Trafalgar Square."),("🇬🇪 You","Brilliant! I'll book that for tomorrow.")],
         "practice":"Plan a perfect 3-day London itinerary with me! Ask about sights, costs and opening times. I'm your tourist guide. 🗼"},
    ]},
    {"week":5,"emoji":"💼","color":"#10b981","title":"სამუშაო და კარიერა","theme":"Work & Career","lessons":[
        {"id":"w5l1","emoji":"🌟","title":"Job Interviews","geo":"სამუშაო ინტერვიუ",
         "scenario":"A job interview at a London tech company. Make a great impression! 🌟",
         "phrases":["I have 3 years of experience in...","My biggest strength is...","I'm looking for a new challenge.","In five years, I see myself...","I work well under pressure.","Do you have any questions for me?"],
         "vocab":[{"w":"candidate","g":"კანდიდატი","p":"კენ-დი-დეიტ"},{"w":"qualification","g":"კვალიფიკაცია","p":"ქვო-ლი-ფი-კეი-შენ"},{"w":"proactive","g":"პროაქტიური","p":"პრო-ექ-თივ"},{"w":"negotiate","g":"მოლაპარაკება","p":"ნი-გო-ში-ეიტ"}],
         "dialogue":[("💼 Interviewer","Tell me a bit about yourself."),("🇬🇪 You","I'm a software developer with 4 years of experience, specialising in Python and web apps."),("💼 Interviewer","Why do you want to work here?"),("🇬🇪 You","Your AI work really excites me. I want to grow in that area."),("💼 Interviewer","Great answer! What's your biggest weakness?")],
         "practice":"I'm interviewing you for a developer position! Answer confidently. Tell me about your experience, strengths and why you want this job. 💼"},
        {"id":"w5l2","emoji":"🖥️","title":"In the Office","geo":"ოფისში",
         "scenario":"First week at a new office. Navigate meetings, small talk and emails! 💬",
         "phrases":["Could you resend that email?","I'll get back to you by end of day.","Can we reschedule the meeting?","CC me on that email.","I'm tied up until 3 PM.","Let's circle back on this."],
         "vocab":[{"w":"deadline","g":"ვადა","p":"დედ-ლაინ"},{"w":"colleague","g":"კოლეგა","p":"კო-ლიგ"},{"w":"feedback","g":"გამოხმაურება","p":"ფიდ-ბეq"},{"w":"agenda","g":"დღის წესრიგი","p":"ა-ჯენ-და"}],
         "dialogue":[("🖥️ Colleague","Hey, did you see my email about the project update?"),("🇬🇪 You","Not yet, sorry — can you resend it? My inbox is a mess!"),("🖥️ Colleague","Sure! Are you free for a quick call at 3?"),("🇬🇪 You","I'm tied up until 3:30. Can we do 4 instead?"),("🖥️ Colleague","Works for me! I'll send a calendar invite.")],
         "practice":"It's Monday morning at the office! Chat with me (your new colleague) about the week, a deadline and let's plan a team lunch. 🖥️"},
        {"id":"w5l3","emoji":"🎓","title":"Learning & Education","geo":"განათლება",
         "scenario":"Chat about your studies, courses and learning goals. 🎓",
         "phrases":["I'm studying for my exam.","I got a distinction!","The lecture was hard to follow.","I learn better by doing.","I'm thinking of doing a Master's.","Can I audit this course?"],
         "vocab":[{"w":"curriculum","g":"სასწავლო გეგმა","p":"კა-რი-კიუ-ლამ"},{"w":"scholarship","g":"სტიპენდია","p":"სქო-ლა-შიპ"},{"w":"thesis","g":"ნაშრომი","p":"თი-სის"},{"w":"distinction","g":"განსხვავება / პატივი","p":"დის-თინq-შენ"}],
         "dialogue":[("🎓 Classmate","How's your English course going?"),("🇬🇪 You","Really well! I'm surprised how much I've improved."),("🎓 Classmate","What helps you most?"),("🇬🇪 You","Watching series without subtitles. It's hard but effective!"),("🎓 Classmate","That's impressive! I should try that.")],
         "practice":"Tell me about your learning journey! Why are you learning English, what methods work, and what are your goals? 🎓"},
        {"id":"w5l4","emoji":"🎤","title":"Presentations","geo":"პრეზენტაციები",
         "scenario":"Give a short work presentation and handle questions from colleagues. 📊",
         "phrases":["Today I'll be talking about...","As you can see from this chart...","Let me take that question.","To summarise...","Any questions so far?","I'd like to hand over to..."],
         "vocab":[{"w":"overview","g":"მიმოხილვა","p":"ო-ვე-ვიუ"},{"w":"highlight","g":"გამოყოფა","p":"ჰაი-ლაიტ"},{"w":"conclude","g":"დასკვნა","p":"კონ-კლუდ"},{"w":"clarify","g":"განმარტება","p":"კლე-რი-ფაი"}],
         "dialogue":[("🎤 You","Good morning everyone. Today I'll be talking about our Q1 results."),("👥 Colleague","Can you share the slides?"),("🎤 You","Of course! As you can see, sales grew by 15%."),("👥 Colleague","What drove that growth?"),("🎤 You","Mainly our new marketing campaign. I'll cover that next.")],
         "practice":"Practice a short 2-minute presentation! Pick any topic and present it to me. I'll ask questions at the end! 🎤"},
    ]},
    {"week":6,"emoji":"🏥","color":"#ef4444","title":"ჯანმრთელობა","theme":"Health & Wellbeing","lessons":[
        {"id":"w6l1","emoji":"🤒","title":"At the Doctor","geo":"ექიმთან",
         "scenario":"You feel unwell and visit a doctor in the UK. Describe your symptoms! 🤒",
         "phrases":["I've had a headache for two days.","My throat is sore.","It hurts when I swallow.","I've been feeling dizzy.","Do I need a prescription?","What medication do you recommend?"],
         "vocab":[{"w":"symptom","g":"სიმპტომი","p":"სიმ-თამ"},{"w":"prescription","g":"რეცეპტი","p":"პრი-სq-რიფ-შენ"},{"w":"diagnosis","g":"დიაგნოზი","p":"დაი-ეგ-ნო-სის"},{"w":"allergy","g":"ალერგია","p":"ე-ლე-ჯი"}],
         "dialogue":[("🏥 Doctor","What seems to be the problem?"),("🇬🇪 You","I've had a bad sore throat for three days. And I feel really tired."),("🏥 Doctor","Any fever?"),("🇬🇪 You","Yes, 38.5 this morning."),("🏥 Doctor","Let me take a look. Open wide...")],
         "practice":"Visit a doctor because you feel unwell! I'm the doctor — describe your symptoms and answer my questions. 🤒"},
        {"id":"w6l2","emoji":"🏋️","title":"Sports & Fitness","geo":"სპორტი",
         "scenario":"Chat with a friend about fitness, sports and staying healthy. 💪",
         "phrases":["I go to the gym three times a week.","I'm training for a marathon.","What's your warm-up routine?","I pulled a muscle yesterday.","I prefer outdoor exercise.","Do you have a personal trainer?"],
         "vocab":[{"w":"workout","g":"ვარჯიში","p":"ვე-q-აუთ"},{"w":"endurance","g":"გამძლეობა","p":"ინ-ჯუ-რენს"},{"w":"stretch","g":"გაწელვა","p":"სთ-რეჩ"},{"w":"stamina","g":"გამძლეობა","p":"სთე-მი-ნა"}],
         "dialogue":[("💪 Friend","You look fit! Do you work out?"),("🇬🇪 You","Thanks! I run every morning and go to the gym twice a week."),("💪 Friend","What's your favourite exercise?"),("🇬🇪 You","Probably swimming. It's easier on the joints."),("💪 Friend","I should try that. I've been having knee problems.")],
         "practice":"Tell me about your fitness routine! What sports do you like? Let's motivate each other! 🏃"},
        {"id":"w6l3","emoji":"💙","title":"Feelings & Emotions","geo":"გრძნობები",
         "scenario":"A heart-to-heart with a good friend about how you've been feeling. 💬",
         "phrases":["I've been feeling a bit overwhelmed.","Things have been stressful lately.","I'm really excited about...","I feel anxious when...","I need some time to myself.","Talking about it helps."],
         "vocab":[{"w":"overwhelmed","g":"გადაბარებული","p":"ო-ვე-ველ-მდ"},{"w":"anxious","g":"შეშფოთებული","p":"ეqნ-შის"},{"w":"content","g":"კმაყოფილი","p":"კონ-თენთ"},{"w":"resilient","g":"გამძლე","p":"რი-ზი-ლიენ-ტ"}],
         "dialogue":[("👫 Friend","You seem a bit quiet today. Everything okay?"),("🇬🇪 You","Honestly, I've been feeling a bit stressed with work."),("👫 Friend","I get that. What's been the hardest part?"),("🇬🇪 You","Just the deadlines. Too many things at once."),("👫 Friend","Have you tried switching off at weekends?")],
         "practice":"Tell me how you've really been feeling lately — happy, stressed, excited, whatever. I'm a good listener! 💙"},
        {"id":"w6l4","emoji":"🚨","title":"Emergencies","geo":"საგანგებო სიტუაციები",
         "scenario":"Something goes wrong — can you handle an emergency in English? 🆘",
         "phrases":["Help! Call an ambulance!","There's been an accident.","My wallet has been stolen.","I need to report a theft.","Is there a hospital nearby?","Please stay calm."],
         "vocab":[{"w":"ambulance","g":"სასწრაფო","p":"ემ-ბიუ-ლენს"},{"w":"emergency","g":"საგანგებო","p":"ი-მე-ჯენ-სი"},{"w":"incident","g":"ინციდენტი","p":"ინ-სი-დენტ"},{"w":"evacuate","g":"ევაკუაცია","p":"ი-ვე-კიუ-ეიტ"}],
         "dialogue":[("🚨 You","Excuse me! My friend has fainted. Please call an ambulance!"),("🏃 Passerby","Of course! I'm calling now. Is he breathing?"),("🚨 You","Yes, but he's not responding."),("🏃 Passerby","Help is on the way. What happened?"),("🚨 You","He suddenly collapsed. We were just walking.")],
         "practice":"Your phone was just stolen on the bus. Report it to me (a police officer) with all the details! 🚨"},
    ]},
    {"week":7,"emoji":"🎉","color":"#f97316","title":"სოციალური ცხოვრება","theme":"Social Life","lessons":[
        {"id":"w7l1","emoji":"📅","title":"Making Plans","geo":"გეგმების დასახვა",
         "scenario":"Arrange a night out — negotiate times, places and activities! 🌆",
         "phrases":["Are you free this weekend?","How about we try that new restaurant?","I'm afraid I can't make it.","Shall we say 8 o'clock?","Let's play it by ear.","Count me in!"],
         "vocab":[{"w":"spontaneous","g":"სპონტანური","p":"სპონ-თეი-ნიეს"},{"w":"tentative","g":"სავარაუდო","p":"თენ-თა-თივ"},{"w":"cancel","g":"გაუქმება","p":"კენ-სელ"},{"w":"convenient","g":"მოსახერხებელი","p":"კო-ნი-ვიენ-ტ"}],
         "dialogue":[("📱 Friend","Hey, are you doing anything Saturday night?"),("🇬🇪 You","Nothing planned! What did you have in mind?"),("📱 Friend","That new cocktail bar just opened downtown."),("🇬🇪 You","Oh, I've heard great things! What time?"),("📱 Friend","Shall we say 8? Can you ask Tom too?")],
         "practice":"Plan a weekend trip with me! Suggest an activity, negotiate the time and place, and deal with my (slightly difficult) schedule! 📅"},
        {"id":"w7l2","emoji":"🥂","title":"At a Party","geo":"წვეულებაზე",
         "scenario":"You're at a housewarming party. Mingle and make conversation! 🥂",
         "phrases":["How do you know the host?","This is a great place!","What do you do for fun?","Have we met before?","Let me get you a drink.","I'm terrible with names, sorry!"],
         "vocab":[{"w":"mingle","g":"ურთიერთობა (ბრბოში)","p":"მინ-გელ"},{"w":"housewarming","g":"სახლის ზეიმი","p":"ჰაუს-ვო-მინ"},{"w":"acquaintance","g":"ნაცნობი","p":"ა-q-ვეინ-თენს"},{"w":"socialise","g":"ურთიერთობა","p":"სო-შა-ლაიზ"}],
         "dialogue":[("🎉 Stranger","Hi! I don't think we've met. I'm Jamie."),("🇬🇪 You","Hey Jamie! I'm Giorgi. How do you know Maria?"),("🎉 Stranger","We used to work together. You?"),("🇬🇪 You","We went to university together, ages ago!"),("🎉 Stranger","Small world! Can I get you something to drink?")],
         "practice":"You're at a party and don't know many people! Start a conversation with me — find out how I know the host and what I do. 🥳"},
        {"id":"w7l3","emoji":"🎬","title":"Movies & Culture","geo":"კინო და კულტურა",
         "scenario":"Discuss a film, book or show with a passionate friend. 🍿",
         "phrases":["Have you seen...?","The plot twist was mind-blowing.","I didn't really get into it.","The acting was outstanding.","I'd give it 8 out of 10.","You should definitely watch it!"],
         "vocab":[{"w":"gripping","g":"მომხიბვლელი","p":"გ-რი-პინ"},{"w":"portrayal","g":"გამოსახვა","p":"პო-თ-რეი-ელ"},{"w":"sequel","g":"გაგრძელება","p":"სი-q-ველ"},{"w":"plot","g":"სიუჟეტი","p":"პლოთ"}],
         "dialogue":[("🎬 Friend","Have you watched anything good lately?"),("🇬🇪 You","Yes! I just finished 'Succession'. Have you seen it?"),("🎬 Friend","No, is it good?"),("🇬🇪 You","It's brilliant — very gripping. The acting is outstanding."),("🎬 Friend","Okay, you've sold me! What's it about?")],
         "practice":"Recommend a film or TV show to me! Tell me the plot, why you loved it and convince me to watch it. 🎬"},
        {"id":"w7l4","emoji":"📱","title":"Phone Calls","geo":"სატელეფონო საუბრები",
         "scenario":"Handle personal and professional phone calls confidently. 📞",
         "phrases":["Could I speak to...?","I'm calling about...","Can I leave a message?","Let me put you on hold.","I'm sorry, you're breaking up.","I'll call you right back."],
         "vocab":[{"w":"voicemail","g":"ხმოვანი შეტყობინება","p":"ვოის-მეილ"},{"w":"extension","g":"შიდა ნომერი","p":"იq-სთენ-შენ"},{"w":"hold","g":"დაბლოკვა (ხაზი)","p":"ჰოლდ"},{"w":"transfer","g":"გადართვა","p":"თ-რენს-ფე"}],
         "dialogue":[("📱 Caller","Good morning, could I speak to the manager please?"),("🇬🇪 You","I'm afraid she's in a meeting. Can I take a message?"),("📱 Caller","Yes please — could she call me back about the contract?"),("🇬🇪 You","Of course. Could I take your name and number?"),("📱 Caller","It's David Clarke, 07700 900123.")],
         "practice":"Practice phone English! Call me to make a doctor's appointment — ask about availability, give your details and confirm the time. Ring ring! 📱"},
    ]},
    {"week":8,"emoji":"🌟","color":"#a855f7","title":"მოწინავე კომუნიკაცია","theme":"Advanced Communication","lessons":[
        {"id":"w8l1","emoji":"🗣️","title":"Opinions & Debates","geo":"მოსაზრებები",
         "scenario":"Discuss a controversial topic and express your views politely. 💬",
         "phrases":["In my opinion...","I see your point, but...","I strongly believe that...","That's an interesting perspective.","I'm on the fence about this.","You've given me a lot to think about."],
         "vocab":[{"w":"perspective","g":"პერსპექტივა","p":"პე-სფეq-თივ"},{"w":"controversial","g":"საკამათო","p":"კონ-თ-რო-ვე-შელ"},{"w":"counterargument","g":"საპასუხო არგუმენტი","p":"კა-ვ-თე-ა-გიუ-მენ-თ"},{"w":"compromise","g":"კომპრომისი","p":"კომ-პ-რო-მაიზ"}],
         "dialogue":[("💬 Friend","Do you think social media is good or bad for society?"),("🇬🇪 You","Honestly, I think it's a double-edged sword."),("💬 Friend","How so?"),("🇬🇪 You","It connects people, but it can also spread misinformation."),("💬 Friend","That's fair. I'm more on the negative side, personally.")],
         "practice":"Let's debate! I'll give a topic and we share opinions. Use 'I strongly believe', 'I see your point, but...' and be politely assertive! 💬"},
        {"id":"w8l2","emoji":"🛍️","title":"Shopping & Bargaining","geo":"შოპინგი",
         "scenario":"Navigate clothing shops, try things on and handle returns! 👗",
         "phrases":["Do you have this in a medium?","Can I try this on?","Where are the changing rooms?","It doesn't quite fit.","Is this the sale price?","I'd like to return this, please."],
         "vocab":[{"w":"refund","g":"ფულის დაბრუნება","p":"რი-ფანდ"},{"w":"receipt","g":"ქვითარი","p":"რი-სიით"},{"w":"fitting room","g":"გასაცმელი","p":"ფი-თინ რუმ"},{"w":"exchange","g":"გაცვლა","p":"იq-ს-ჩეინჯ"}],
         "dialogue":[("🇬🇪 You","Excuse me, do you have this jacket in navy blue?"),("🛍️ Staff","Let me check... Yes! In what size?"),("🇬🇪 You","Medium, please. Can I try it on?"),("🛍️ Staff","Of course, the fitting rooms are on the left."),("🇬🇪 You","Great, thanks!")],
         "practice":"Go shopping! I'm a shop assistant. Ask about sizes, try things on, then try to return something from last week. 🛍️"},
        {"id":"w8l3","emoji":"📰","title":"News & Current Events","geo":"სიახლეები",
         "scenario":"Discuss a news story with a colleague over morning coffee. 📱",
         "phrases":["Did you hear about...?","Apparently, it's because...","That's quite alarming.","I read that...","What's your take on it?","It's more complicated than it seems."],
         "vocab":[{"w":"headline","g":"სათაური","p":"ჰედ-ლაინ"},{"w":"coverage","g":"გაშუქება","p":"კა-ვე-რეჯ"},{"w":"bias","g":"მიკერძოება","p":"ბა-ეს"},{"w":"correspondent","g":"კორესპონდენტი","p":"კო-ე-სფ-ო-ნ-დენ-ტ"}],
         "dialogue":[("☕ Colleague","Did you see the news this morning?"),("🇬🇪 You","About the election? Yes! What did you think?"),("☕ Colleague","Honestly, I was surprised. I didn't expect that result."),("🇬🇪 You","Me neither. What's your take on what happens next?"),("☕ Colleague","I think it's more complicated than the media makes out.")],
         "practice":"Tell me about something interesting you heard or read recently — local news, tech, sport, anything. Let's chat! 📰"},
        {"id":"w8l4","emoji":"✉️","title":"Formal Writing & Emails","geo":"ოფიციალური წერა",
         "scenario":"Write professional emails — job applications, complaints, enquiries. 💻",
         "phrases":["I am writing with regard to...","Please find attached...","I would be grateful if...","I look forward to hearing from you.","Should you require any further information...","Kind regards,"],
         "vocab":[{"w":"correspondence","g":"მიმოწერა","p":"კო-ე-სფ-ო-ნ-დენს"},{"w":"enquiry","g":"შეკითხვა (ოფ.)","p":"ინ-q-ვა-ი-ი"},{"w":"acknowledge","g":"დასტური","p":"ეq-ნო-ლეჯ"},{"w":"concise","g":"ლაკონური","p":"კონ-საის"}],
         "dialogue":[("💻 You","Subject: Application for Software Developer Position"),("💻 You","Dear Hiring Manager,"),("💻 You","I am writing to apply for the position advertised on your website."),("💻 You","Please find my CV attached. I look forward to hearing from you."),("💻 You","Kind regards, Giorgi")],
         "practice":"Write a professional email with me! Tell me the situation (job application, complaint, enquiry) and I'll help you write it step by step. ✉️"},
    ]},
]

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="English Learning App",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)

# ══════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
.main .block-container { max-width: 860px; padding: 1.5rem 1rem; }

/* ── login page ── */
.auth-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 2rem 2rem 1.5rem;
    margin: 1rem 0;
}

/* ── page hero ── */
.page-hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 1.8rem 2rem 1.4rem;
    margin-bottom: 1.5rem;
    color: #fff;
}
.page-hero h1 { font-size: 1.9rem; font-weight: 800; margin: 0 0 .3rem; letter-spacing: -.5px; }
.page-hero p  { font-size: .95rem; opacity: .65; margin: 0; }

/* ── user badge in sidebar ── */
.user-badge {
    background: linear-gradient(135deg, rgba(99,102,241,.3), rgba(139,92,246,.3));
    border: 1px solid rgba(99,102,241,.4);
    border-radius: 16px;
    padding: .9rem 1rem;
    margin-bottom: .8rem;
    text-align: center;
}
.user-avatar {
    width: 52px; height: 52px;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; font-weight: 800; color: #fff;
    margin: 0 auto .5rem;
}
.user-name  { font-size: 1rem; font-weight: 700; color: #e0e7ff; }
.user-uname { font-size: .78rem; color: rgba(255,255,255,.45); }

/* ── backup box ── */
.backup-box {
    background: rgba(16,185,129,.1);
    border: 1px solid rgba(52,211,153,.25);
    border-radius: 12px;
    padding: .7rem .9rem;
    font-size: .78rem;
    color: #a7f3d0;
    word-break: break-all;
    margin: .4rem 0;
}

/* ── word cards ── */
.word-card {
    background: linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);
    border-radius: 20px; padding: 1.3rem 1.4rem 1rem;
    margin: .8rem 0; color: #fff;
    box-shadow: 0 8px 32px rgba(99,102,241,.35);
    border: 1px solid rgba(255,255,255,0.15);
}
.word-card.known {
    background: linear-gradient(135deg,#10b981 0%,#059669 100%);
    box-shadow: 0 6px 20px rgba(16,185,129,.3); opacity:.8;
}
.review-card {
    background: linear-gradient(135deg,#f43f5e 0%,#e11d48 100%);
    border-radius: 20px; padding: 1.3rem 1.4rem 1rem;
    margin: .8rem 0; color: #fff;
    box-shadow: 0 8px 32px rgba(244,63,94,.35);
    border: 1px solid rgba(255,255,255,0.15);
}
.word-badge {
    display: inline-block; background: rgba(255,255,255,0.2);
    border-radius: 30px; padding: .15rem .7rem;
    font-size: .7rem; font-weight: 600; letter-spacing: .5px;
    text-transform: uppercase; margin-bottom: .6rem;
}
.word-title    { font-size: 1.5rem; font-weight: 800; letter-spacing: -.3px; margin-bottom: .15rem; }
.word-phonetic { font-size: .9rem; opacity: .6; font-style: italic; margin-bottom: .4rem; letter-spacing: .5px; }
.word-trans    { font-size: 1rem; opacity: .85; font-weight: 500; margin-bottom: .5rem; }
.word-def      { font-size: .88rem; opacity: .8; margin-bottom: .5rem; line-height: 1.5; }
.word-example  {
    font-size: .82rem; opacity: .7; font-style: italic;
    background: rgba(0,0,0,0.15); border-radius: 10px;
    padding: .5rem .75rem; line-height: 1.5;
}

/* ── stat boxes ── */
.stat-box {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px; padding: 1.2rem .8rem; text-align: center;
}
.stat-label { font-size: .78rem; color: rgba(255,255,255,.5); margin-top: .3rem; text-transform: uppercase; letter-spacing: .5px; }
.stat-num         { font-size: 2.2rem; font-weight: 800; color: #a5b4fc; }
.stat-num.green   { color: #34d399; }
.stat-num.red     { color: #fb7185; }

/* ── banners ── */
.banner-info {
    background: linear-gradient(135deg,rgba(59,130,246,.3),rgba(6,182,212,.3));
    border: 1px solid rgba(99,179,237,.3); color: #e0f2fe;
    border-radius: 16px; padding: 1rem 1.2rem; margin: .6rem 0; line-height: 1.7;
}
.banner-ok {
    background: linear-gradient(135deg,rgba(16,185,129,.3),rgba(5,150,105,.3));
    border: 1px solid rgba(52,211,153,.3); color: #d1fae5;
    border-radius: 16px; padding: 1rem 1.2rem; margin: .6rem 0;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1e1b4b 0%,#0f0c29 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,.85) !important; }

/* ── buttons ── */
.stButton > button {
    border-radius: 12px !important; font-weight: 600 !important;
}

/* ── chat ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important; margin: .4rem 0 !important;
}

/* ── text ── */
h1,h2,h3,h4,p,span,label,.stMarkdown { color: rgba(255,255,255,.9) !important; }
.stCaption { color: rgba(255,255,255,.45) !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }

@media (max-width:640px) {
    .page-hero h1 { font-size: 1.4rem; }
    .word-title   { font-size: 1.2rem; }
    .main .block-container { padding: .6rem .4rem; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  DATABASE (Supabase)
# ══════════════════════════════════════════════
def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def _sb_headers() -> dict:
    key = st.secrets["SUPABASE_KEY"]
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

def _sb_url(table: str) -> str:
    return f"{st.secrets['SUPABASE_URL']}/rest/v1/{table}"

def _get_user(username: str) -> dict | None:
    r = requests.get(
        _sb_url("users"),
        headers=_sb_headers(),
        params={"username": f"eq.{username}", "select": "*"},
    )
    data = r.json()
    return data[0] if isinstance(data, list) and data else None

def _username_exists(username: str) -> bool:
    r = requests.get(
        _sb_url("users"),
        headers=_sb_headers(),
        params={"username": f"eq.{username}", "select": "id"},
    )
    data = r.json()
    return isinstance(data, list) and len(data) > 0

def save_user_data():
    if not st.session_state.get("logged_in"):
        return
    try:
        requests.patch(
            _sb_url("users"),
            headers=_sb_headers(),
            params={"username": f"eq.{st.session_state.current_user}"},
            json={
                "dictionary":        st.session_state.dictionary,
                "known_words":       st.session_state.known_words,
                "review_list":       st.session_state.review_list,
                "completed_lessons": st.session_state.completed_lessons,
            },
        )
    except Exception:
        pass

# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
def _init():
    defaults = {
        "logged_in":          False,
        "current_user":       "",
        "display_name":       "",
        "dictionary":         [],
        "known_words":        [],
        "review_list":        [],
        "chat_history":       [],
        "scanned_text":       "",
        "scanned_words":      [],
        "completed_lessons":  [],
        "lesson_week":        None,
        "lesson_id":          None,
        "lesson_chat":        [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ══════════════════════════════════════════════
#  ANTHROPIC CLIENT
# ══════════════════════════════════════════════
@st.cache_resource
def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# ══════════════════════════════════════════════
#  LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════
def page_auth():
    st.markdown("""
    <div class="page-hero" style="text-align:center;">
        <h1>📚 English Learning</h1>
        <p>AI-powered ინგლისურის სასწავლო პლატფორმა</p>
    </div>
    """, unsafe_allow_html=True)

    tab_in, tab_reg, tab_restore = st.tabs(["🔑 შესვლა", "✨ რეგისტრაცია", "♻️ ბაზის აღდგენა"])

    # ── შესვლა ──
    with tab_in:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        uname = st.text_input("მომხმარებლის სახელი", key="li_u", placeholder="username")
        passw = st.text_input("პაროლი", type="password", key="li_p")
        if st.button("შესვლა →", type="primary", use_container_width=True, key="li_btn"):
            if not uname or not passw:
                st.error("შეავსე ყველა ველი")
            else:
                user = _get_user(uname.strip().lower())
                if not user:
                    st.error("❌ მომხმარებელი ვერ მოიძებნა")
                elif user["password_hash"] != _hash_pw(passw):
                    st.error("❌ პაროლი არასწორია")
                else:
                    st.session_state.logged_in         = True
                    st.session_state.current_user      = uname.strip().lower()
                    st.session_state.display_name      = user["display_name"]
                    st.session_state.dictionary        = user.get("dictionary") or []
                    st.session_state.known_words       = user.get("known_words") or []
                    st.session_state.review_list       = user.get("review_list") or []
                    st.session_state.completed_lessons = user.get("completed_lessons") or []
                    st.session_state.chat_history      = []
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── რეგისტრაცია ──
    with tab_reg:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        disp  = st.text_input("სახელი (ნებისმიერი)", key="rg_d", placeholder="მაგ: გიორგი")
        uname_r = st.text_input("Username (ლათინური, პატარა)", key="rg_u", placeholder="მაგ: giorgi")
        pw1   = st.text_input("პაროლი", type="password", key="rg_p1")
        pw2   = st.text_input("პაროლის გამეორება", type="password", key="rg_p2")
        if st.button("რეგისტრაცია →", type="primary", use_container_width=True, key="rg_btn"):
            if not all([disp, uname_r, pw1, pw2]):
                st.error("შეავსე ყველა ველი")
            elif pw1 != pw2:
                st.error("❌ პაროლები არ ემთხვევა")
            elif len(pw1) < 4:
                st.error("❌ პაროლი მინიმუმ 4 სიმბოლო")
            elif not re.match(r'^[a-z0-9_]+$', uname_r.lower()):
                st.error("❌ Username-ში მხოლოდ ლათინური ასოები, ციფრები და _ ")
            else:
                if _username_exists(uname_r.lower()):
                    st.error("❌ ეს username უკვე გამოყენებულია")
                else:
                    try:
                        r = requests.post(
                            _sb_url("users"),
                            headers=_sb_headers(),
                            json={
                                "username":      uname_r.lower(),
                                "password_hash": _hash_pw(pw1),
                                "display_name":  disp,
                                "created_at":    str(datetime.date.today()),
                                "dictionary":    [],
                                "known_words":   [],
                                "review_list":   [],
                            },
                        )
                        if r.status_code in (200, 201):
                            st.success("✅ რეგისტრაცია წარმატებულია! გადადი 'შესვლა' tab-ზე.")
                        else:
                            st.error(f"❌ შეცდომა: {r.text}")
                    except Exception as e:
                        st.error(f"❌ შეცდომა: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ბაზის აღდგენა ──
    with tab_restore:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.info("მონაცემები Supabase-ში ინახება — ავტომატურად უსაფრთხოა.\n\n"
                "პაროლის დავიწყების შემთხვევაში დაუკავშირდი ადმინს.")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  AUTH GATE
# ══════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
    st.stop()


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def _to_base64(f) -> str:
    return base64.standard_b64encode(f.getvalue()).decode("utf-8")

def _parse_json_words(text: str):
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return None

def _is_known(word: str) -> bool:
    return word.lower() in st.session_state.known_words

def _add_to_dictionary(words: list) -> int:
    existing = {w["word"].lower() for w in st.session_state.dictionary}
    added = 0
    for w in words:
        if w["word"].lower() not in existing:
            st.session_state.dictionary.append(w)
            existing.add(w["word"].lower())
            added += 1
    if added:
        save_user_data()
    return added

def _tokenize_words(text: str) -> list:
    seen, result = set(), []
    for w in re.findall(r"[a-zA-Z']+", text):
        wc = w.strip("'")
        if len(wc) >= 4:
            k = wc.lower()
            if k not in seen:
                seen.add(k); result.append(wc)
    return result


# ══════════════════════════════════════════════
#  ANTHROPIC FUNCTIONS
# ══════════════════════════════════════════════
def analyze_image(uploaded_file):
    client = get_client()
    b64 = _to_base64(uploaded_file)
    prompt = (
        "Please read every word in this image carefully.\n"
        "Then pick exactly 5 interesting English words at B1–C1 level.\n\n"
        "Return ONLY a valid JSON array:\n"
        '[\n  {\n    "word": "example",\n'
        '    "georgian_phonetic": "ეგზამპლ",\n'
        '    "georgian_translation": "მაგალითი",\n'
        '    "english_definition": "A single sentence.",\n'
        '    "context_example": "Exact sentence from image."\n  }\n]\n\n'
        "Rules: exactly 5 words, georgian_phonetic uses Georgian letters for English sound, output only JSON."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=1500,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": uploaded_file.type, "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    raw = msg.content[0].text
    return _parse_json_words(raw), raw

def extract_all_text(uploaded_file) -> str:
    client = get_client()
    b64 = _to_base64(uploaded_file)
    msg = client.messages.create(
        model=MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": uploaded_file.type, "data": b64}},
            {"type": "text", "text": "Transcribe ALL text in this image exactly as written. Output only the text."},
        ]}],
    )
    return msg.content[0].text.strip()

def define_words(word_list: list, context: str) -> list:
    client = get_client()
    words_str = ", ".join(f'"{w}"' for w in word_list)
    prompt = (
        f'Text:\n"""\n{context}\n"""\n\n'
        f"Define these words: {words_str}\n\n"
        "Return ONLY a JSON array:\n"
        '[\n  {\n    "word": "example",\n'
        '    "georgian_phonetic": "ეგზამპლ",\n'
        '    "georgian_translation": "მაგალითი",\n'
        '    "english_definition": "A single sentence.",\n'
        '    "context_example": "Sentence from text."\n  }\n]\n'
        "Output only JSON."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_words(msg.content[0].text) or []

def chat_with_teacher(user_msg: str, history: list) -> str:
    client = get_client()
    system = (
        "You are a friendly English teacher. Talk in simple, clear English. "
        "If the user makes a grammar mistake, correct it simply, explain the rule in 1 sentence, "
        "then continue the conversation.\n\n"
        "Format corrections:\n"
        "✏️ Correction: [corrected sentence]\n"
        "📌 Rule: [one-sentence explanation]\n\n"
        "Keep responses concise and encouraging."
    )
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_msg})
    resp = client.messages.create(model=MODEL, max_tokens=800, system=system, messages=messages)
    return resp.content[0].text


# ══════════════════════════════════════════════
#  RENDER CARD
# ══════════════════════════════════════════════
def _render_card(word_data: dict, card_class: str, card_key: str, show_buttons: bool = True):
    word     = word_data.get("word", "")
    phonetic = word_data.get("georgian_phonetic", "")
    trans    = word_data.get("georgian_translation", "")
    defn     = word_data.get("english_definition", "")
    ex       = word_data.get("context_example", "")
    word_l   = word.lower()
    is_known = _is_known(word)

    phonetic_html = f'<div class="word-phonetic">[ {phonetic} ]</div>' if phonetic else ""
    badge = "✅ ვიცი" if is_known else "📖 ახალი სიტყვა"

    st.markdown(f"""
    <div class="{card_class}{'  known' if is_known else ''}">
        <div class="word-badge">{badge}</div>
        <div class="word-title">{word}</div>
        {phonetic_html}
        <div class="word-trans">🇬🇪 {trans}</div>
        <div class="word-def">💡 {defn}</div>
        <div class="word-example">"{ex}"</div>
    </div>
    """, unsafe_allow_html=True)

    safe = word.replace("'", "\\'").replace('"', "&quot;")
    if st.button(f"🔊 გამოთქმა — {word}", key=f"speak_{card_key}", use_container_width=True):
        components.html(
            f"<script>var u=new SpeechSynthesisUtterance('{safe}');u.lang='en-US';u.rate=0.82;"
            "speechSynthesis.cancel();speechSynthesis.speak(u);</script>",
            height=0,
        )

    if not show_buttons:
        return

    col1, col2 = st.columns(2)
    with col1:
        lbl = "✅ ვიცი ✓" if is_known else "✅ ვიცი"
        if st.button(lbl, key=f"know_{card_key}", use_container_width=True,
                     type="primary" if is_known else "secondary"):
            if word_l not in st.session_state.known_words:
                st.session_state.known_words.append(word_l)
            st.session_state.review_list = [r for r in st.session_state.review_list
                                             if r["word"].lower() != word_l]
            save_user_data()
            st.rerun()
    with col2:
        if st.button("❌ არ ვიცი", key=f"dontknow_{card_key}", use_container_width=True):
            st.session_state.known_words = [w for w in st.session_state.known_words if w != word_l]
            if word_l not in [r["word"].lower() for r in st.session_state.review_list]:
                st.session_state.review_list.append(word_data)
            save_user_data()
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: VISION
# ══════════════════════════════════════════════
def page_vision():
    st.markdown("""
    <div class="page-hero">
        <h1>📷 ტექსტის დამუშავება</h1>
        <p>ატვირთე ტექსტიანი სურათი — ავტომატურად ან სიტყვები თავად აირჩიე</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("რეჟიმი:", ["🤖 ავტომატური (5 სიტყვა)", "✋ ხელით არჩევა"],
                    horizontal=True, key="vision_mode_radio")
    uploaded = st.file_uploader("სურათის ატვირთვა", type=["jpg","jpeg","png","webp"],
                                help="მობილურზე კამერა გაიხსნება")

    if uploaded is None:
        st.markdown("""<div class="banner-info">
            📱 <strong>გამოყენება:</strong><br>
            1. აირჩიე რეჟიმი ზემოთ<br>
            2. ატვირთე სურათი ტექსტით<br>
            3. <strong>ავტომატური</strong> — Claude 5 საუკეთესო სიტყვას ამოარჩევს<br>
            4. <strong>ხელით</strong> — ტექსტი ამოდის, შენ ირჩევ
        </div>""", unsafe_allow_html=True)
        return

    st.image(uploaded, caption="ატვირთული სურათი", use_container_width=True)

    if mode == "🤖 ავტომატური (5 სიტყვა)":
        if st.button("🔍 სიტყვების ამოღება", type="primary", use_container_width=True):
            with st.spinner("Claude კითხულობს სურათს…"):
                try:
                    words, raw = analyze_image(uploaded)
                except anthropic.AuthenticationError:
                    st.error("❌ API გასაღები არასწორია.")
                    return
                except Exception as exc:
                    st.error(f"❌ შეცდომა: {exc}")
                    return
            if not words:
                st.error("ვერ მოხერხდა JSON-ის წაკითხვა.")
                with st.expander("Raw პასუხი"):
                    st.code(raw)
                return
            added = _add_to_dictionary(words)
            st.markdown(f"""<div class="banner-ok">✨ ნაპოვნია <strong>{len(words)}</strong> სიტყვა —
                <strong>{added}</strong> ახალი დაემატა ლექსიკონს!</div>""", unsafe_allow_html=True)
            for i, w in enumerate(words):
                _render_card(w, "word-card", f"vision_{i}", show_buttons=False)
    else:
        c1, c2 = st.columns([3,1])
        with c1:
            scan = st.button("🔎 ტექსტის სკანირება", type="primary", use_container_width=True)
        with c2:
            if st.button("🗑️", use_container_width=True, help="სკანირების გასუფთავება"):
                st.session_state.scanned_text = ""; st.session_state.scanned_words = []; st.rerun()

        if scan:
            with st.spinner("Claude ტექსტს კითხულობს…"):
                try:
                    raw_text = extract_all_text(uploaded)
                except Exception as exc:
                    st.error(f"❌ {exc}"); st.stop()
            st.session_state.scanned_text  = raw_text
            st.session_state.scanned_words = _tokenize_words(raw_text)

        if st.session_state.scanned_text:
            with st.expander("📄 ამოღებული ტექსტი", expanded=False):
                st.text(st.session_state.scanned_text)
            if not st.session_state.scanned_words:
                st.warning("სურათში ინგლისური სიტყვები ვერ მოიძებნა."); return

            selected = st.multiselect(
                "📌 აირჩიე სიტყვები რომელთა სწავლა გინდა:",
                options=st.session_state.scanned_words,
                placeholder="დააწკაპე სიტყვებზე…",
                key="manual_sel",
            )
            if selected:
                if st.button(f"📖 {len(selected)} სიტყვის განმარტება",
                             type="primary", use_container_width=True, key="def_btn"):
                    with st.spinner("Claude განმარტებებს ამზადებს…"):
                        try:
                            words = define_words(selected, st.session_state.scanned_text)
                        except Exception as exc:
                            st.error(f"❌ {exc}"); st.stop()
                    if not words:
                        st.error("Claude-მა ვერ დაამუშავა."); return
                    added = _add_to_dictionary(words)
                    st.markdown(f"""<div class="banner-ok">✨ <strong>{added}</strong> ახალი სიტყვა დაემატა!</div>""",
                                unsafe_allow_html=True)
                    for i, w in enumerate(words):
                        _render_card(w, "word-card", f"man_{i}", show_buttons=False)


# ══════════════════════════════════════════════
#  PAGE: DICTIONARY
# ══════════════════════════════════════════════
def page_dictionary():
    st.markdown("""
    <div class="page-hero">
        <h1>📚 ჩემი ლექსიკონი</h1>
        <p>შენი შენახული სიტყვები — ავტომატურად ინახება ფაილში</p>
    </div>
    """, unsafe_allow_html=True)

    total    = len(st.session_state.dictionary)
    known_n  = len(st.session_state.known_words)
    review_n = len(st.session_state.review_list)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{total}</div>'
                    '<div class="stat-label">სულ სიტყვა</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num green">{known_n}</div>'
                    '<div class="stat-label">ვიცი</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num red">{review_n}</div>'
                    '<div class="stat-label">გასამეორებელი</div></div>', unsafe_allow_html=True)

    st.divider()

    if total == 0:
        st.info("ლექსიკონი ცარიელია.\n\nგადადი **📷 ტექსტის დამუშავება** გვერდზე!")
        return

    if review_n > 0:
        with st.expander(f"🔄 გასამეორებელი სიტყვები ({review_n})", expanded=True):
            for i, w in enumerate(st.session_state.review_list):
                _render_card(w, "review-card", f"rev_{i}")

    st.subheader(f"ყველა სიტყვა ({total})")
    filt = st.selectbox("ფილტრი:", ["ყველა", "მხოლოდ ვიცი", "მხოლოდ არ ვიცი"], key="dict_filter")

    for i, w in enumerate(st.session_state.dictionary):
        is_known = _is_known(w["word"])
        if filt == "მხოლოდ ვიცი"   and not is_known: continue
        if filt == "მხოლოდ არ ვიცი" and is_known:     continue
        _render_card(w, "word-card", f"dict_{i}")


# ══════════════════════════════════════════════
#  PAGE: CHAT
# ══════════════════════════════════════════════
def page_chat():
    st.markdown("""
    <div class="page-hero">
        <h1>💬 სალაპარაკო გრამატიკა</h1>
        <p>ესაუბრე AI მასწავლებელს — გრამატიკის შეცდომებს ავტომატურად გაასწორებს</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown("Hello! 👋 I'm your friendly English teacher. How are you today? "
                        "Feel free to write anything in English! 😊")

    if user_input := st.chat_input("Write in English… / დაწერე ინგლისურად…"):
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("…"):
                try:
                    reply = chat_with_teacher(user_input, st.session_state.chat_history)
                except anthropic.AuthenticationError:
                    reply = "❌ API გასაღები არასწორია."
                except Exception as exc:
                    reply = f"❌ შეცდომა: {exc}"
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "user",      "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    if st.session_state.chat_history:
        if st.button("🗑️ საუბრის გასუფთავება", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: LESSONS
# ══════════════════════════════════════════════
def _save_completed():
    try:
        requests.patch(
            _sb_url("users"), headers=_sb_headers(),
            params={"username": f"eq.{st.session_state.current_user}"},
            json={"completed_lessons": st.session_state.completed_lessons},
        )
    except Exception:
        pass

def page_lessons():
    completed = st.session_state.completed_lessons

    # ── Lesson detail view ──
    if st.session_state.lesson_id:
        lesson = next((l for w in CURRICULUM for l in w["lessons"] if l["id"] == st.session_state.lesson_id), None)
        week_data = next((w for w in CURRICULUM for l in w["lessons"] if l["id"] == st.session_state.lesson_id), None)
        if not lesson:
            st.session_state.lesson_id = None; st.rerun(); return

        if st.button("← კვირის გაკვეთილები", key="back_to_week"):
            st.session_state.lesson_id = None; st.session_state.lesson_chat = []; st.rerun()

        is_done = lesson["id"] in completed
        st.markdown(f"""
        <div class="page-hero" style="background:linear-gradient(135deg,{week_data['color']}33,{week_data['color']}11);">
            <h1>{lesson['emoji']} {lesson['title']}</h1>
            <p>🇬🇪 {lesson['geo']} &nbsp;·&nbsp; {"✅ დასრულებული" if is_done else "📖 შეუსრულებელი"}</p>
        </div>""", unsafe_allow_html=True)

        st.markdown(f'<div class="banner-info">📍 <strong>სცენარი:</strong> {lesson["scenario"]}</div>', unsafe_allow_html=True)

        # Phrases
        st.subheader("💬 ძირითადი ფრაზები")
        c1, c2 = st.columns(2)
        for i, ph in enumerate(lesson["phrases"]):
            with (c1 if i % 2 == 0 else c2):
                st.markdown(f'<div style="background:rgba(255,255,255,.06);border-radius:12px;padding:.55rem .9rem;margin:.25rem 0;border-left:3px solid {week_data["color"]};font-size:.9rem;">"{ph}"</div>', unsafe_allow_html=True)

        st.divider()

        # Vocab
        st.subheader("📝 ვოკაბულარი")
        v1, v2 = st.columns(2)
        for i, v in enumerate(lesson["vocab"]):
            with (v1 if i % 2 == 0 else v2):
                safe_w = v['w'].replace("'", "\\'")
                st.markdown(f"""<div style="background:rgba(255,255,255,.05);border-radius:14px;padding:.75rem 1rem;margin:.3rem 0;border:1px solid rgba(255,255,255,.1);">
                    <div style="font-size:1.05rem;font-weight:700;color:#a5b4fc;">{v['w']}</div>
                    <div style="font-size:.78rem;color:rgba(255,255,255,.45);">[{v['p']}]</div>
                    <div style="font-size:.88rem;color:#c4b5fd;margin-top:.2rem;">🇬🇪 {v['g']}</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"🔊 {v['w']}", key=f"vs_{lesson['id']}_{i}", use_container_width=True):
                    components.html(f"<script>var u=new SpeechSynthesisUtterance('{safe_w}');u.lang='en-US';u.rate=0.82;speechSynthesis.cancel();speechSynthesis.speak(u);</script>", height=0)

        st.divider()

        # Dialogue
        st.subheader("🎭 მინი-დიალოგი")
        for speaker, line in lesson["dialogue"]:
            is_you = "You" in speaker or "🇬🇪" in speaker
            align = "flex-end" if is_you else "flex-start"
            bg = f"{week_data['color']}55" if is_you else "rgba(255,255,255,.07)"
            st.markdown(f'<div style="display:flex;justify-content:{align};margin:.3rem 0;"><div style="max-width:75%;background:{bg};border-radius:16px;padding:.55rem .9rem;"><div style="font-size:.7rem;opacity:.5;margin-bottom:.15rem;">{speaker}</div><div style="font-size:.9rem;">{line}</div></div></div>', unsafe_allow_html=True)

        st.divider()

        # Practice chat
        st.subheader("🤖 Claude-თან პრაქტიკა")
        st.markdown(f'<div class="banner-info">🎯 {lesson["practice"]}</div>', unsafe_allow_html=True)

        for msg in st.session_state.lesson_chat:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if not st.session_state.lesson_chat:
            with st.chat_message("assistant"):
                st.markdown(f"Ready to practice? 😊 {lesson['practice']}")

        if user_input := st.chat_input("Write in English… / დაწერე ინგლისურად…", key="lc_input"):
            with st.chat_message("user"):
                st.markdown(user_input)
            with st.chat_message("assistant"):
                with st.spinner("…"):
                    try:
                        system = (
                            f"You are a friendly English teacher running a practice scenario.\n"
                            f"Scenario: {lesson['scenario']}\nGoal: {lesson['practice']}\n"
                            f"Key phrases: {', '.join(lesson['phrases'][:4])}\n\n"
                            "Engage the student naturally in the scenario. If they make grammar mistakes, "
                            "correct gently: ✏️ Correction: [corrected]\n📌 Rule: [brief rule]\n"
                            "Stay in character. Keep it fun and encouraging!"
                        )
                        msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.lesson_chat]
                        msgs.append({"role": "user", "content": user_input})
                        reply = get_client().messages.create(model=MODEL, max_tokens=600, system=system, messages=msgs).content[0].text
                    except Exception as exc:
                        reply = f"❌ შეცდომა: {exc}"
                st.markdown(reply)
            st.session_state.lesson_chat.append({"role": "user", "content": user_input})
            st.session_state.lesson_chat.append({"role": "assistant", "content": reply})

        st.divider()
        col_done, col_rst = st.columns([3, 1])
        with col_done:
            if not is_done:
                if st.button("✅ გაკვეთილი დასრულებულია!", type="primary", use_container_width=True, key="mark_done"):
                    st.session_state.completed_lessons.append(lesson["id"])
                    _save_completed()
                    st.success("🎉 გაკვეთილი ჩაითვალა დასრულებულად!")
                    st.balloons()
                    st.rerun()
            else:
                st.markdown('<div class="banner-ok">✅ ეს გაკვეთილი უკვე დასრულებულია!</div>', unsafe_allow_html=True)
        with col_rst:
            if is_done and st.button("↩️", use_container_width=True, key="undone", help="გასუფთავება"):
                st.session_state.completed_lessons = [x for x in st.session_state.completed_lessons if x != lesson["id"]]
                _save_completed(); st.rerun()
        return

    # ── Week lesson list ──
    if st.session_state.lesson_week is not None:
        week = CURRICULUM[st.session_state.lesson_week]
        if st.button("← ყველა კვირა", key="back_to_weeks"):
            st.session_state.lesson_week = None; st.rerun()

        done_count = sum(1 for l in week["lessons"] if l["id"] in completed)
        st.markdown(f"""<div class="page-hero" style="background:linear-gradient(135deg,{week['color']}33,{week['color']}11);">
            <h1>{week['emoji']} კვირა {week['week']}: {week['title']}</h1>
            <p>{week['theme']} · {done_count}/4 გაკვეთილი დასრულებულია</p>
        </div>""", unsafe_allow_html=True)

        for lesson in week["lessons"]:
            is_done = lesson["id"] in completed
            cc, cb = st.columns([4, 1])
            with cc:
                st.markdown(f"""<div style="{'opacity:.7;' if is_done else ''}background:rgba(255,255,255,.06);border-radius:16px;
                    padding:.9rem 1.2rem;border:1px solid {week['color']}44;margin:.35rem 0;">
                    <div style="font-size:1.1rem;font-weight:700;">{"✅" if is_done else "📖"} {lesson['emoji']} {lesson['title']}</div>
                    <div style="font-size:.83rem;opacity:.55;margin-top:.15rem;">🇬🇪 {lesson['geo']}</div>
                </div>""", unsafe_allow_html=True)
            with cb:
                st.write("")
                if st.button("✅" if is_done else "▶ Start", key=f"open_{lesson['id']}", use_container_width=True):
                    st.session_state.lesson_id = lesson["id"]; st.session_state.lesson_chat = []; st.rerun()
        return

    # ── Week overview ──
    total = sum(len(w["lessons"]) for w in CURRICULUM)
    done  = sum(1 for w in CURRICULUM for l in w["lessons"] if l["id"] in completed)
    pct   = int(done / total * 100) if total else 0

    st.markdown(f"""<div class="page-hero">
        <h1>📖 ინგლისური 8 კვირაში</h1>
        <p>სასაუბრო ინგლისური · {done}/{total} გაკვეთილი · {pct}% პროგრესი</p>
    </div>""", unsafe_allow_html=True)
    st.progress(done / total if total else 0, text=f"{pct}% კურსის პროგრესი")
    st.divider()

    for i in range(0, len(CURRICULUM), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            if i + j >= len(CURRICULUM): break
            w = CURRICULUM[i + j]
            wd = sum(1 for l in w["lessons"] if l["id"] in completed)
            with col:
                st.markdown(f"""<div style="background:linear-gradient(135deg,{w['color']}22,{w['color']}11);
                    border:1px solid {w['color']}44;border-radius:20px;padding:1.2rem 1.3rem;margin:.3rem 0;min-height:130px;">
                    <div style="font-size:2rem;margin-bottom:.3rem;">{w['emoji']}</div>
                    <div style="font-size:.72rem;opacity:.45;text-transform:uppercase;letter-spacing:.5px;">კვირა {w['week']}</div>
                    <div style="font-size:1.05rem;font-weight:700;color:#e0e7ff;margin:.2rem 0;">{w['title']}</div>
                    <div style="font-size:.82rem;opacity:.55;margin-bottom:.7rem;">{w['theme']}</div>
                    <div style="background:rgba(255,255,255,.1);border-radius:10px;height:5px;">
                        <div style="background:{w['color']};width:{wd*25}%;height:5px;border-radius:10px;"></div>
                    </div>
                    <div style="font-size:.72rem;opacity:.45;margin-top:.3rem;">{wd}/4 გაკვეთილი</div>
                </div>""", unsafe_allow_html=True)
                if st.button(f"კვირა {w['week']} →", key=f"wk_{w['week']}", use_container_width=True):
                    st.session_state.lesson_week = i + j; st.rerun()


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    initials = st.session_state.display_name[:1].upper() if st.session_state.display_name else "?"
    st.markdown(f"""
    <div class="user-badge">
        <div class="user-avatar">{initials}</div>
        <div class="user-name">{st.session_state.display_name}</div>
        <div class="user-uname">@{st.session_state.current_user}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    page = st.radio("გვერდი:", [
        "📖 გაკვეთილები",
        "📷 ტექსტის დამუშავება",
        "📚 ჩემი ლექსიკონი",
        "💬 სალაპარაკო გრამატიკა",
    ], key="nav_page")
    st.divider()

    total_l = sum(len(w["lessons"]) for w in CURRICULUM)
    done_l  = len(st.session_state.completed_lessons)
    st.metric("გაკვეთილები", f"{done_l}/{total_l}")
    st.metric("სიტყვები",       len(st.session_state.dictionary))
    st.metric("გასამეორებელი", len(st.session_state.review_list))
    st.divider()

    st.caption("☁️ მონაცემები Supabase-ში ინახება")
    if st.button("💾 ხელით შენახვა", use_container_width=True):
        save_user_data()
        st.success("შენახულია!")

    st.divider()
    if st.button("🚪 გამოსვლა", use_container_width=True):
        save_user_data()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════
if   page == "📖 გაკვეთილები":           page_lessons()
elif page == "📷 ტექსტის დამუშავება":   page_vision()
elif page == "📚 ჩემი ლექსიკონი":       page_dictionary()
elif page == "💬 სალაპარაკო გრამატიკა": page_chat()
